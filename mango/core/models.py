import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel


class Apps(BaseModel):
  name: str
  name_plural: str
  label: str
  label_plural: str
  list_url: str
  is_active: bool
