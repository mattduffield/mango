import jwt
import os
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from mango.auth.models import AuthHandler, Credentials, NotAuthenticatedException
from mango.auth.forms import LoginForm
from mango.db.models import QueryOne, InsertOne
from mango.db.api import find_one_sync, find_one, insert_one
from settings import manager, templates

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY')
# DATABASE_CLUSTER = os.environ.get('DATABASE_CLUSTER')
# DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
# DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DATABASE_NAME')


router = APIRouter(
  prefix = '/auth',
  tags = ['Authorization']
)

auth_handler = AuthHandler()

# manager = LoginManager(SESSION_SECRET_KEY, token_url='/auth/login', use_cookie=True)
# manager.cookie_name = 'mango-cookie'
# manager.not_authenticated_exception = NotAuthenticatedException

@manager.user_loader
def load_user(email:str):
  result = {
    'collection': 'users', 
    'query': {
      'email': email
    }, 
    'database': DATABASE_NAME
  }
  query = QueryOne.parse_obj(result)
  found = find_one_sync(query)
  return found

@router.get('/login', response_class=HTMLResponse)
def login(request: Request, next: Optional[str] = None):
  context = {'request': request}
  response = templates.TemplateResponse('auth/login.html', context)
  return response

@router.post('/login')
# def login(request: Request, email: str = Form(...), password: str = Form(...), next: Optional[str] = None):
async def login(request: Request, next: Optional[str] = None):
  form = await LoginForm.from_formdata(request)
  credentials = Credentials(**form.data)
  user = load_user(credentials.email)
  if not user:
    raise InvalidCredentialsException
  elif not auth_handler.verify_password(credentials.password, user['password']):
    raise InvalidCredentialsException
  if next is None:
    next = '/'
  access_token = manager.create_access_token(
    data={'sub': credentials.email}
  )
  # resp = RedirectResponse(url='/private', status_code=status.HTTP_302_FOUND)
  resp = RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
  manager.set_cookie(resp, access_token)
  return resp


# @router.post('/login')
# def login(credentials: Credentials, next: Optional[str] = None):
#   user = load_user(credentials.email)
#   if not user:
#     raise InvalidCredentialsException
#   elif not auth_handler.verify_password(credentials.password, user['password']):
#     raise InvalidCredentialsException
#   if next is None:
#     next = '/'
#   access_token = manager.create_access_token(
#     data={'sub': credentials.email}
#   )
#   # resp = RedirectResponse(url='/private', status_code=status.HTTP_302_FOUND)
#   resp = RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
#   manager.set_cookie(resp, access_token)
#   return resp

@router.get('/private')
def handle_private(_=Depends(manager)):
  return 'You are an authenticated user!'

@router.post('/register', status_code=201)
async def register(credentials: Credentials):
  hashed_password = auth_handler.get_password_hash(credentials.password)
  #
  # TODO: NEED TO MAKE THIS PART GENERIC BY PASSING IN THE REQUEST DATA...
  #
  result = {
    'collection': 'users', 
    'data': {
      'email': credentials.email,
      'password': hashed_password
    }, 
    'database': DATABASE_NAME
  }
  query = InsertOne.parse_obj(result)
  try:
    resp = await insert_one(query)
    return resp
  except:
    raise HTTPException(status_code=404, detail='User already exists')

@router.post('/server-signin')
async def server_signin():
  serverEmail = 'server@server.com'
  token = auth_handler.encode_token(serverEmail)
  return {'token': token, 'database': None, 'user': serverEmail}

@router.post('/signin')
async def signin(credentials: Credentials):
  result = {
    'collection': 'users', 
    'query': {
      'email': credentials.email
    }, 
    'database': DATABASE_NAME
  }
  query = QueryOne.parse_obj(result)
  found = await find_one(query)
  if (found) and (auth_handler.verify_password(credentials.password, found['password'])):
    user_id = found['_id']
    # email = credentials.email
    # username = found['username']    
    # {user_id: _id, email, username, database}
    token = auth_handler.encode_token(user_id)
    return {'token': token, 'database': DATABASE_NAME, 'user': found}
  else:
    raise HTTPException(status_code=404, detail='Invalid credentials')
