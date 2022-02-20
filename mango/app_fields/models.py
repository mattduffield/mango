from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel
from pydantic.types import PositiveInt


class AppField(BaseModel):
  app_id: str
  name: str
  label: str
  data_type: str
  object_type: Optional[str] # Only if there data_type is 'object'
  default_value: Optional[str]
  default_value_use_quotes: bool
  element_type: str
  element_html: Optional[str]
  choices: List[Dict[str, str]] = []
  validators: List[str] = []
  element_attributes: dict = {}
  is_active: bool

  def __str__(self):
    return self.label
  
  class Meta:
    model_name = 'app_fields'
    model_name_plural = 'app_fields'
    search_index_name = 'fields_search'
    search_fields = [
      'label'
    ]
    order_by = [
      'label',
    ]
    page_size = 0
