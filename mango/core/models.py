import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel


class App(BaseModel):
  name: str
  name_plural: str
  label: str
  label_plural: str
  list_url: str
  list_route_name: str
  is_active: bool
