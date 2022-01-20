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
  str_func: str


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
  default_value_use_quotes: bool
  element_type: str
  validators: List[str]
  element_attributes: dict
  is_active: bool


class PageLayout(BaseModel):
  field_type: str
  name: str
  css_class: Optional[str]
  css_class_use_quotes: Optional[bool]
  label_class: Optional[str]
  label_class_use_quotes: Optional[bool]
  page_layout: List['PageLayout']


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
  page_layout: List[PageLayout]
  is_active: bool
