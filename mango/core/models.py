import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)

class Funcs(BaseModel):
  __str__: str

class Meta(BaseModel):
  search_index_name: str
  search_by: str
  order_by: List[str]
  page_size: int


class Field(BaseModel):
  name: str
  label: str
  data_type: str
  default_value: Optional[str]
  is_active: bool


class App(BaseModel):
  name: str
  name_plural: str
  label: str
  label_plural: str
  list_url: str
  list_route_name: str
  fields: List[Field]
  meta: Meta
  funcs: Funcs
  is_active: bool
