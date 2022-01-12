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
from mango.db.models import QueryOne, InsertOne
from mango.db.api import find_one_sync, find_one, insert_one_sync, insert_one
from mango.wf.models import WorkflowRequest
from mango.wf.views import init_workflow_run
from settings import manager, templates

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY')
DATABASE_NAME = os.environ.get('DATABASE_NAME')


router = APIRouter(
  prefix = '/auth',
  tags = ['Authorization']
)

auth_handler = AuthHandler()

# def add_user(email:str, password:str, database):
#   hashed_password = auth_handler.get_password_hash(password)
#   payload = {
#     'database': database,
#     'collection': 'users', 
#     'insert_type': 'insert_one',
#     'data': {
#       'email': email,
#       'password': hashed_password,
#     }, 
#   }
#   query = InsertOne.parse_obj(payload)
#   try:
#     resp = insert_one_sync(query)
#     return resp
#   except:
#     raise HTTPException(status_code=404, detail='User already exists')

@manager.user_loader(database=DATABASE_NAME)
def load_user(email:str, database):
  payload = {
    'database': database,
    'collection': 'users', 
    'query_type': 'find_one',
    'query': {
      'email': email
    }, 
  }
  query = QueryOne.parse_obj(payload)
  found = find_one_sync(query)
  return found

@router.get('/login', response_class=HTMLResponse)
def login(request: Request, next: Optional[str] = None):
  context = {'request': request}
  response = templates.TemplateResponse('auth/login.html', context)
  return response

@router.post('/login')
async def login(request: Request, next: Optional[str] = None):
  form = await LoginForm.from_formdata(request)
  credentials = Credentials(**form.data)
  user = load_user(credentials.email, database=DATABASE_NAME)
  if not user or not auth_handler.verify_password(credentials.password, user['password']):
    context = {'request': request}
    context['form'] = form
    response = templates.TemplateResponse('auth/login.html', context)
    return response
  # if not user:
  #   raise InvalidCredentialsException
  # elif not auth_handler.verify_password(credentials.password, user['password']):
  #   raise InvalidCredentialsException

  if next is None:
    next = '/'
  access_token = manager.create_access_token(
    data={'sub': credentials.email},
    expires=timedelta(hours=12),
  )
  resp = RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
  manager.set_cookie(resp, access_token)
  return resp

@router.get('/logout', response_class=HTMLResponse)
def logout(request: Request, next: Optional[str] = None):
  resp = RedirectResponse(url='login', status_code=status.HTTP_302_FOUND)
  resp.delete_cookie('mango-cookie')
  # manager.set_cookie(resp, '') # Need to clear out the cookie
  return resp

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
    # result = add_user(credentials.email, credentials.password, database=DATABASE_NAME)
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


  # forgotPassword(options) {
  #   let opt = {
  #     "database": options.company_id,
  #     "name": "ResetPassword",
  #     "trigger": "send reset password",
  #     "data": options,
  #   };
  #   const payload = {method: 'post', body: JSON.stringify(opt)};
  #   return this.workflowFetch(`init-workflow-run`, payload)
  #     .then(response => response.json())
  #     .then(data => {
  #       if (data.error) {
  #         throw data.error;
  #       }
  #       return data;
  #     });
  # }




# # @router.get('/private')
# # def handle_private(_=Depends(manager)):
# #   return 'You are an authenticated user!'

# @router.post('/register', status_code=201)
# async def register(credentials: Credentials):
#   hashed_password = auth_handler.get_password_hash(credentials.password)
#   #
#   # TODO: NEED TO MAKE THIS PART GENERIC BY PASSING IN THE REQUEST DATA...
#   #
#   result = {
#     'collection': 'users', 
#     'data': {
#       'email': credentials.email,
#       'password': hashed_password
#     }, 
#     'database': DATABASE_NAME
#   }
#   query = InsertOne.parse_obj(result)
#   try:
#     resp = await insert_one(query)
#     return resp
#   except:
#     raise HTTPException(status_code=404, detail='User already exists')

@router.post('/server-signin')
async def server_signin():
  serverEmail = 'server@server.com'
  token = auth_handler.encode_token(serverEmail)
  return {'token': token, 'database': None, 'user': serverEmail}

# @router.post('/signin')
# async def signin(credentials: Credentials):
#   result = {
#     'collection': 'users', 
#     'query': {
#       'email': credentials.email
#     }, 
#     'database': DATABASE_NAME
#   }
#   query = QueryOne.parse_obj(result)
#   found = await find_one(query)
#   if (found) and (auth_handler.verify_password(credentials.password, found['password'])):
#     user_id = found['_id']
#     # email = credentials.email
#     # username = found['username']    
#     # {user_id: _id, email, username, database}
#     token = auth_handler.encode_token(user_id)
#     return {'token': token, 'database': DATABASE_NAME, 'user': found}
#   else:
#     raise HTTPException(status_code=404, detail='Invalid credentials')
