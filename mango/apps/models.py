from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel
from pydantic.types import PositiveInt


class Funcs(BaseModel):
  str_func: str
  object_display: str


class MetaData(BaseModel):
  search_index_name: str
  search_fields: Optional[List[str]] = []
  order_by: List[str]
  page_size: int


class Field(BaseModel):
  name: str
  label: str
  data_type: str
  default_value: Optional[str]
  default_value_use_quotes: bool
  element_type: str
  element_html: Optional[str]
  choices: List[Dict[str, str]] = []
  validators: List[str] = []
  element_attributes: dict = {}
  fields: Optional[List['Field']]
  is_active: bool

  def __str__(self):
    return self.name
  
  class Meta:
    model_name = 'app'
    model_name_plural = 'apps'
    search_index_name = 'apps_search'
    search_fields = [
      'name',
      'name_plural',
    ]
    order_by = [
      'name',
    ]
    page_size = 10


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
  stage: Optional[str]
  is_active: bool

  def __str__(self):
    return self.name
  
  class Meta:
    model_name = 'app'
    model_name_plural = 'apps'
    search_index_name = 'apps_search'
    search_fields = [
      'name',
      'name_plural',
    ]
    order_by = [
      'label',
    ]
    page_size = 10
