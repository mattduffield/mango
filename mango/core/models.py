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
  object_display: str


class MetaData(BaseModel):
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
  validators: List[str] = []
  element_attributes: dict = {}
  fields: Optional[List['Field']]
  is_active: bool


class TableHeader(BaseModel):
  name: str = ''
  html: str = ''
  actions: Optional[List[str]]
  css_class: str = ''
  css_class_use_quotes: bool = True
  format: str = ''


class TableBody(BaseModel):
  name: str = ''
  html: str = ''
  actions: Optional[List[str]]
  css_class: str = ''
  css_class_use_quotes: bool = True
  format: str = ''


class ListLayout(BaseModel):
  table_header: Optional[List[TableHeader]]
  table_body: Optional[List[TableBody]]


class PageLayout(BaseModel):
  field_type: str
  name: str = ''
  content: str = ''
  css_class: str = ''
  css_class_use_quotes: bool = True
  label_class: str = ''
  label_class_use_quotes: bool = True
  page_layout: Optional[List['PageLayout']]


class App(BaseModel):
  name: str
  name_plural: str
  label: str
  label_plural: str
  list_url: str
  list_route_name: str
  fields: List[Field]
  meta_data: MetaData
  funcs: Funcs
  page_layout: List[PageLayout]
  list_layout: ListLayout
  is_active: bool
