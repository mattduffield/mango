import jwt
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel

from mango.db.query import QueryOne, InsertOne
from mango.db.api import find_one, insert_one

DATABASE_CLUSTER = os.environ.get('DATABASE_CLUSTER')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DATABASE_NAME')


class Credentials(BaseModel):
  email: str
  password: str


class AuthHandler():
  security = HTTPBearer()
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  secret = 'hwdrvkhxro_PGxQN3tarEA'  # TODO: NEED TO GET THIS FROM ENVIRONMENT VARIABLE

  def get_password_hash(self, password):
    return self.pwd_context.hash(password)

  def verify_password(self, plain_password, hashed_password):
    return self.pwd_context.verify(plain_password, hashed_password)

  def encode_token(self, user_id):
    payload = {
      'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
      'iat': datetime.utcnow(),
      'sub': user_id
    }
    return jwt.encode(
      payload,
      self.secret,
      algorithm='HS256'
    )

  def decode_token(self, token):
    try:
      payload = jwt.decode(token, self.secret, algorithms=['HS256'])
      return payload['sub']
    except jwt.ExpiredSignatureError:
      raise HTTPException(status_code=401, detail='Signature has expired')
    except jwt.InvalidTokenError:
      raise HTTPException(status_code=401, detail='Invalid token')

  def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
    return self.decode_token(auth.credentials)

router = APIRouter(
  prefix = '/auth',
  tags = ['Authorization']
)

auth_handler = AuthHandler()

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
