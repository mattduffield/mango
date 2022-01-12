from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from enum import Enum, IntEnum
from pydantic import BaseModel
from hooks.models import Hook
import hooks.views

class QueryModel(BaseModel):
  entity_name: str
  get: Optional[str] # 123
  filter: Optional[dict] # order_by, start_position, max_results, **kwargs
  all: Optional[dict] # order_by, start_position, max_results=100
  where: Optional[dict] # where_clause, order_by, start_position, max_results
  query: Optional[str] # SELECT * FROM ...
  count: Optional[str] # where_clause


class CreateModel(BaseModel):
  entity_name: str
  data: dict


class UpdateModel(BaseModel):
  entity_name: str
  entity_id: str
  data: dict


class NewNoteAttachment(BaseModel):
  entity_name: str
  entity_id: str
  note: str


class NewAttachment(BaseModel):
  entity_name: str
  entity_id: str
