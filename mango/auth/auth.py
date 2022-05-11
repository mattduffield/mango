from datetime import timedelta
import jwt
import os
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from mango.auth.models import AuthHandler, Credentials, Signup, PasswordReset
from mango.auth.forms import LoginForm, SignupForm, PasswordResetForm
from mango.db.models import QueryOne, InsertOne, AggregatePipeline
from mango.db.rest import find_one_sync, find_one, insert_one_sync, insert_one, run_pipeline_sync
from mango.wf.models import WorkflowRequest
from mango.wf.views import init_workflow_run
from settings import manager, templates

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

headers = {}
# headers = {'HX-Refresh': 'true'}

router = APIRouter(
  prefix = '/auth',
  tags = ['Authorization']
)

auth_handler = AuthHandler()


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
      }
    ],
    cursor={},
  )
  role_list_result = run_pipeline_sync(ap)
  [user] = role_list_result['cursor']['firstBatch']
  if user:
    for role in user['user_roles']:
      user['action_list'] = user['action_list'] + role['action_list']
  return user

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
  [user] = role_list_result['cursor']['firstBatch']
  if user:
    for role in user['user_roles']:
      user['action_list'] = user['action_list'] + role['action_list']
  return user

def can(current_user, role:str = '', action:str = ''):
  result = False
  if current_user:
    if role and action:
      result = role in current_user.get('role_list', []) and action in current_user.get('action_list', [])
    elif action:
      result = action in current_user.get('action_list', [])
    elif role:
        result = role in current_user.get('role_list', [])
  return result

def can_can(request:Request, role:str = '', action:str = ''):
  result = False
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
  context = {'request': request}
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
    context = {'request': request}
    context['form'] = form
    response = templates.TemplateResponse('auth/login.html', context)
    return response

  if next is None:
    next = '/'
  access_token = manager.create_access_token(
    data={'sub': credentials.email},
    expires=timedelta(hours=12),
    scopes=user['action_list'],
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
  context = {'request': request}
  response = templates.TemplateResponse('auth/password_reset_complete.html', context)
  return response

@router.get('/password-reset-done', response_class=HTMLResponse, name='password-reset-done')
async def get_password_reset_done(request: Request):
  context = {'request': request}
  response = templates.TemplateResponse('auth/password_reset_done.html', context)
  return response

@router.get('/signup-confirmation', response_class=HTMLResponse, name='signup-confirmation')
async def get_signup_confirmation(request: Request):
  context = {'request': request}
  response = templates.TemplateResponse('auth/signup_confirmation.html', context)
  return response

@router.get('/signup-approval-complete', response_class=HTMLResponse, name='signup-approval-complete')
async def get_signup_confirmation(request: Request):
  context = {'request': request}
  response = templates.TemplateResponse('auth/signup_approval_complete.html', context)
  return response

@router.get('/signup-rejection-complete', response_class=HTMLResponse, name='signup-rejection-complete')
async def get_signup_confirmation(request: Request):
  context = {'request': request}
  response = templates.TemplateResponse('auth/signup_rejection_complete.html', context)
  return response

@router.get('/signup', response_class=HTMLResponse, name='signup')
async def get_signup(request: Request, next: Optional[str] = None):
  context = {'request': request}
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
    context = {'request': request}
    context['form'] = form
    response = templates.TemplateResponse('auth/signup.html', context)
    return response

@router.get('/password-reset', response_class=HTMLResponse, name='password-reset')
async def get_password_reset(request: Request, next: Optional[str] = None):
  context = {'request': request}
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
    context = {'request': request}
    context['form'] = form
    response = templates.TemplateResponse('auth/password_reset_form.html', context)
    return response

@router.post('/server-signin')
async def server_signin():
  serverEmail = 'server@server.com'
  token = auth_handler.encode_token(serverEmail)
  return {'token': token, 'database': None, 'user': serverEmail}
