from datetime import timedelta
import jwt
import os
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from mango.auth.models import AuthHandler, Credentials, Signup, PasswordReset, NotAuthenticatedException
from mango.auth.forms import LoginForm, SignupForm, PasswordResetForm
from mango.db.models import Query, QueryOne, InsertOne, AggregatePipeline
from mango.db.rest import find_one_sync, find_one, insert_one_sync, insert_one, run_pipeline_sync
from mango.wf.models import WorkflowRequest
from mango.wf.views import init_workflow_run
from mango.template_utils.utils import configure_templates

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
TEMPLATE_DIRECTORY = os.environ.get('TEMPLATE_DIRECTORY')
templates = configure_templates(directory=TEMPLATE_DIRECTORY)

manager = LoginManager(
  SESSION_SECRET_KEY, 
  token_url='/auth/login', 
  use_cookie=True,
  cookie_name='mango-cookie',
  default_expiry=timedelta(hours=12),
)
manager.not_authenticated_exception = NotAuthenticatedException


headers = {}
# headers = {'HX-Refresh': 'true'}

router = APIRouter(
  prefix = '/auth',
  tags = ['Authorization']
)

auth_handler = AuthHandler()


def get_query(query_type: str, collection: str, query: dict = {}, sort: dict = {}, data: dict = None):
  if query_type == 'find_one':
    query = QueryOne(
      database=DATABASE_NAME,
      collection=collection,
      query=query  # {'_id': self._id}
    )
  elif query_type == 'find':
    query = Query(
      database=DATABASE_NAME,
      collection=collection,
      query=query,  # {'_id': self._id}
      sort=sort  # {'name': 1}
    )
  return query

def get_default_organization():
  query = get_query('find_one', collection='organization', query={'is_default': True})
  data = find_one_sync(query)
  return data


@manager.user_loader(database=DATABASE_NAME)
def load_user(email:str, database):
  ap = AggregatePipeline(
    database=database,
    aggregate='user',
    pipeline=[
      {
        '$match': {
          'email': email,
          'is_active': True
        }
      },
      {
        '$project': {
          'password': 0
        }
      },
      {
        '$lookup': {
          'from': 'role',
          'localField': 'role_list',
          'foreignField': 'name',
          'as': 'user_roles'
        }
      },
      {
        '$lookup': {
          'from': 'profile_maker',
          'localField': 'profile_id',
          'foreignField': '_id',
          'as': 'user_profile'
        }
      },
      {
        "$unwind": "$user_profile"
      },
      {
        '$lookup': {
          'from': 'action',
          'pipeline': [],
          'as': 'actions'
        }
      },
      {
        '$lookup': {
          'from': 'role',
          'pipeline': [],
          'as': 'roles'
        }
      },
      {
        "$lookup": { 
          "from": "menu_maker", 
          "pipeline": [ 
            { "$match": { "$expr": { "$eq": [ "$is_active", True ] }}},
            { "$project": { "label": 1, "is_top_level": 1, "role_list": 1, "screen_list": 1 } }
          ], "as": "menus" 
        } 
      },
      {
        "$lookup": { 
          "from": "screen_maker", 
          "pipeline": [ 
            { "$match": { "$expr": { "$eq": [ "$is_active", True ] }}},
            { "$project": { "name": 1, "route_prefix": 1 } }
          ], "as": "screens" 
        } 
      },
      {
        "$lookup": { 
          "from": "screen_builder", 
          "pipeline": [ 
            { "$match": { "$expr": { "$eq": [ "$is_active", True ] }}},
            { "$project": { "name": 1, "route_prefix": 1 } }
          ], "as": "screen_builder_list" 
        } 
      },
    ],
    cursor={},
  )
  role_list_result = run_pipeline_sync(ap)
  if any(role_list_result['cursor']['firstBatch']):
    [user] = role_list_result['cursor']['firstBatch']
    if user:
      for role in user['user_roles']:
        user['action_list'] = user['action_list'] + role['action_list']
      for role in user['user_profile']['role_list']:
        role_item = next((x for x in user['roles'] if x['name'] == role), None)
        user['action_list'] = user['action_list'] + role_item['action_list']
      user['action_list'] = user['action_list'] + user['user_profile']['action_list']
      for menu in user['user_profile']['menu_list']:
        m = next((x for x in user['menus'] if x['_id'] == menu['menu_id']), None)
        if m:
          menu['label'] = m.get('label', 'UNKNOWN')
          menu['is_top_level'] = m.get('is_top_level', False)
          menu['screen_list'] = m.get('screen_list', [])
          for scr in menu['screen_list']:
            if 'screen_builder_list' in user and 'screen_builder_id' in scr:
              sb_prefix = next((x.get('route_prefix', 'x') for x in user['screen_builder_list'] if x['_id'] == scr['screen_builder_id']), None)
              if sb_prefix:
                scr['route_prefix'] = sb_prefix
              else:  
                scr['route_prefix'] = next((x.get('route_prefix', 'screen') for x in user['screens'] if x['_id'] == scr['screen_id']), None)
            else:  
              scr['route_prefix'] = next((x.get('route_prefix', 'screen') for x in user['screens'] if x['_id'] == scr['screen_id']), None)
    # Find all top-level
    top_level_list = [x for x in user['user_profile']['menu_list'] if x.get('is_top_level', False) == True]
    default_screen = None
    for entry in top_level_list:
      if default_screen:
        break
      for screen in entry['screen_list']:
        is_default_route = screen.get('screen_is_default_route', False)
        if is_default_route:
          default_screen = screen
          break
    user['user_profile']['default_screen'] = default_screen
    return user
  return None

def authenticate_user(email:str, database):
  ap = AggregatePipeline(
    database=database,
    aggregate='user',
    pipeline=[
      {
        '$match': {
          'email': email,
          'is_active': True
        }
      },
      {
        '$lookup': {
          'from': 'role',
          'localField': 'role_list',
          'foreignField': 'name',
          'as': 'user_roles'
        }
      }
    ],
    cursor={},
  )
  role_list_result = run_pipeline_sync(ap)
  if any(role_list_result['cursor']['firstBatch']):
    [user] = role_list_result['cursor']['firstBatch']
    if user:
      for role in user['user_roles']:
        user['action_list'] = user['action_list'] + role['action_list']
    return user
  return None

def can(current_user, role:str = '', action:str = ''):
  result = True
  if current_user:
    if role and action:
      result = role in current_user.get('role_list', []) and action in current_user.get('action_list', [])
    elif action:
      result = action in current_user.get('action_list', [])
    elif role:
        result = role in current_user.get('role_list', [])
  return result

def can_can(request:Request, role:str = '', action:str = ''):
  result = True
  current_user = request.state.user
  if current_user:
    if role and action:
      result = role in current_user.get('role_list', []) and action in current_user.get('action_list', [])
    elif action:
      result = action in current_user.get('action_list', [])
    elif role:
        result = role in current_user.get('role_list', [])
  return result

@router.get('/login', response_class=HTMLResponse)
def login(request: Request, next: Optional[str] = None):
  global headers
  # headers = {'HX-Refresh': 'true'}
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  response = templates.TemplateResponse('auth/login.html', context, headers=headers)
  return response

@router.post('/login')
async def login(request: Request, next: Optional[str] = None):
  global headers
  # headers = {'HX-Refresh': 'false'}
  form = await LoginForm.from_formdata(request)
  credentials = Credentials(**form.data)
  user = authenticate_user(credentials.email, database=DATABASE_NAME)
  if not user or not auth_handler.verify_password(credentials.password, user['password']):
    view = { 'lookups': {'current_organization': get_default_organization() } }
    context = {'request': request, 'view': view}
    context['form'] = form
    response = templates.TemplateResponse('auth/login_invalid.html', context)
    return response

  if next is None:
    next = '/'
  access_token = manager.create_access_token(
    data={'sub': credentials.email},
    # expires=timedelta(seconds=10),
    expires=timedelta(hours=12),
  )
  resp = RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
  manager.set_cookie(resp, access_token)
  return resp

@router.get('/logout', response_class=HTMLResponse)
def logout(request: Request, next: Optional[str] = None):
  resp = RedirectResponse(url='login', status_code=status.HTTP_302_FOUND)
  resp.delete_cookie('mango-cookie')
  return resp

@router.get('/password-reset-complete', response_class=HTMLResponse, name='password-reset-complete')
async def get_password_reset_complete(request: Request):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  response = templates.TemplateResponse('auth/password_reset_complete.html', context)
  return response

@router.get('/password-reset-done', response_class=HTMLResponse, name='password-reset-done')
async def get_password_reset_done(request: Request):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  response = templates.TemplateResponse('auth/password_reset_done.html', context)
  return response

@router.get('/signup-confirmation', response_class=HTMLResponse, name='signup-confirmation')
async def get_signup_confirmation(request: Request):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  response = templates.TemplateResponse('auth/signup_confirmation.html', context)
  return response

@router.get('/signup-approval-complete', response_class=HTMLResponse, name='signup-approval-complete')
async def get_signup_confirmation(request: Request):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  response = templates.TemplateResponse('auth/signup_approval_complete.html', context)
  return response

@router.get('/signup-rejection-complete', response_class=HTMLResponse, name='signup-rejection-complete')
async def get_signup_confirmation(request: Request):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  response = templates.TemplateResponse('auth/signup_rejection_complete.html', context)
  return response

@router.get('/signup', response_class=HTMLResponse, name='signup')
async def get_signup(request: Request, next: Optional[str] = None):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  form = await SignupForm.from_formdata(request)
  context['form'] = form
  response = templates.TemplateResponse('auth/signup.html', context)
  return response

@router.post('/signup')
async def post_signup(request: Request, next: Optional[str] = None):
  form = await SignupForm.from_formdata(request)
  if await form.validate_on_submit():
    signup = Signup(**form.data)
    signup.password = auth_handler.get_password_hash(signup.password)
    wr = WorkflowRequest(
      database=DATABASE_NAME,
      name='UserSignup',
      trigger='signup',
      data=dict(signup),
    )
    res = await init_workflow_run(wr)
    resp = RedirectResponse(url='signup-confirmation', status_code=status.HTTP_302_FOUND)
    return resp
  else:
    view = { 'lookups': {'current_organization': get_default_organization() } }
    context = {'request': request, 'view': view}
    context['form'] = form
    response = templates.TemplateResponse('auth/signup.html', context)
    return response

@router.get('/password-reset', response_class=HTMLResponse, name='password-reset')
async def get_password_reset(request: Request, next: Optional[str] = None):
  view = { 'lookups': {'current_organization': get_default_organization() } }
  context = {'request': request, 'view': view}
  form = await PasswordResetForm.from_formdata(request)
  context['form'] = form
  response = templates.TemplateResponse('auth/password_reset_form.html', context)
  return response

@router.post('/password-reset')
async def post_password_reset(request: Request, next: Optional[str] = None):
  form = await PasswordResetForm.from_formdata(request)
  if await form.validate_on_submit():
    reset = PasswordReset(**form.data)
    wr = WorkflowRequest(
      database=DATABASE_NAME,
      name='ResetPassword',
      trigger='send_reset_password',
      data=dict(reset),
    )
    res = await init_workflow_run(wr)
    resp = RedirectResponse(url='password-reset-done', status_code=status.HTTP_302_FOUND)
    return resp
  else:
    view = { 'lookups': {'current_organization': get_default_organization() } }
    context = {'request': request, 'view': view}
    context['form'] = form
    response = templates.TemplateResponse('auth/password_reset_form.html', context)
    return response

@router.post('/server-signin')
async def server_signin():
  serverEmail = 'server@server.com'
  token = auth_handler.encode_token(serverEmail)
  return {'token': token, 'database': None, 'user': serverEmail}
