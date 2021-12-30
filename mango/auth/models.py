import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel

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


class Credentials(BaseModel):
  email: str
  password: str
