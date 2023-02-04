import decimal
import inspect
from bson import Decimal128
import bson.timestamp
import bson.objectid
import json, re
from decimal import *
from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from enum import Enum, IntEnum
from fastapi import File, Form
from pydantic import BaseModel, conlist, Field, Json
from pymongo import (
  InsertOne as BulkInsertOne, 
  DeleteOne as BulkDeleteOne,
  DeleteMany as BulkDeleteMany,
  ReplaceOne as BulkReplaceOne,
  UpdateOne as BulkUpdateOne,
  UpdateMany as BulkUpdateMany,
)
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


class DateTimeAwareEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, datetime):
      return o.isoformat()
    return json.JSONEncoder.default(self, o)


# https://www.geeksforgeeks.org/convert-pymongo-cursor-to-json/
def json_from_mongo(x):
  if isinstance(x, datetime):
    return x.isoformat()
  elif isinstance(x, bson.objectid.ObjectId):
    return str(x)
  elif isinstance(x, Decimal128):
    return str(x)
  elif isinstance(x, dict) and '$oid' in x:
    return x['$oid']
  elif isinstance(x, dict) and '$date' in x:
    return x['$date']
  elif isinstance(x, dict) and '$numberDecimal' in x:
    original_places = 2
    actual_places = str(x['$numberDecimal'])[::-1].find('.')
    if actual_places > original_places:
      places = actual_places
    else:
      places = original_places
    exp = decimal.Decimal(".1") ** places
    raw = decimal.Decimal(x['$numberDecimal'])
    quantized = raw.quantize(exp)
    return str(quantized)
  else:
    return x

def json_to_mongo(dct):
  # if '_id' in dct and type(dct['_id']) is str:
  #   dct['_id'] = ObjectId(dct['_id'])
  ids = [key for (key,value) in dct.items() if key.endswith('_id') and value]
  for key in ids:
    if type(dct[key]) is str:
      dct[key] = ObjectId(dct[key])
  if dct.get('$set'):
    set_ids = [key for (key,value) in dct['$set'].items() if key.endswith('_id') and value]
    for key in set_ids:
      if dct['$set'][key] and type(dct['$set'][key]) is str:
        dct['$set'][key] = ObjectId(dct['$set'][key])
  return dct

def datetime_parser(dct):
  for (k, v) in dct.items():
    if type(v) is str and re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d*$', v):
      dct[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
    elif type(v) is str and re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', v):
      dct[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
    else:
      pass

  return dct

# def json_from_mongo(dct):
#   if '_id' in dct and '$oid' in dct['_id']:
#     dct['_id'] = dct['_id']['$oid']
#   if '$date' in dct and isinstance(dct['$date'], datetime):
#     return dct['$date'].__str__()
#   # if isinstance(dct['$date'], (datetime)):
#   #   dct['$date'] = dct['$date'].isoformat()
#   return dct

def mongo_to_json(dct):
  if isinstance(dct, bson.objectid.ObjectId):
    return str(dct)
  elif isinstance(dct, bson.timestamp.Timestamp):
    return str(dct)
  elif isinstance(dct, bytes):
    return str(dct)
  elif isinstance(dct, datetime):
    return dct.isoformat()
  elif isinstance(dct, Decimal128):
    return Decimal(dct)
  elif '_id' in dct and '$oid' in dct['_id']:
    dct['_id'] = dct['_id']['$oid']
  elif '$date' in dct and isinstance(dct['$date'], datetime):
    return dct['$date'].__str__()
  return dct


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
            annotation=field.outer_type_,
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls

# class Credentials(BaseModel):
#   email: str
#   password: str

class BaseMongo(BaseModel):
  database: str 
  collection: str

class QueryOne(BaseMongo):
  query_type: Literal['find_one', 'find'] = 'find_one'
  query: Optional[dict]
  projection: Optional[dict]
  sort: Optional[dict]
  skip: Optional[int]
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    expr = f'entity.{self.query_type}({self.query}'
    if self.projection and any(self.projection):
      projection_pairs = self.projection.items()
      expr += ', {'
      for key, value in projection_pairs:
        expr += f'"{key}": {int(value)}, '
      expr += '}'
    if self.sort and self.sort.items():
      sort_pairs = self.sort.items()
      expr += f', sort=['
      for key, value in sort_pairs:
        expr += f'("{key}", {int(value)}),'
      expr = expr[:-1]
      expr += f']'
    if self.skip:
      expr += f', skip={self.skip}'
    expr += f')'
    return expr

@as_form
class Query(QueryOne):
  query_type: Literal['find_one', 'find'] = 'find'
  limit: Optional[int]
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    expr = f'entity.{self.query_type}({self.query}'
    if self.projection and any(self.projection):
      projection_pairs = self.projection.items()
      expr += ', {'
      for key, value in projection_pairs:
        expr += f'"{key}": {int(value)}, '
      expr += '}'
    if self.sort and self.sort.items():
      sort_pairs = self.sort.items()
      expr += f', sort=['
      for key, value in sort_pairs:
        expr += f'("{key}", {int(value)}),'
      expr = expr[:-1]
      expr += f']'
    if self.skip:
      expr += f', skip={self.skip}'
    if self.query_type == 'find':
      if self.limit:
        expr += f', limit={self.limit}'
    expr += f')'
    return expr

@as_form
class Count(BaseMongo):
  query: Optional[dict]
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    expr = f'entity.count_documents({self.query})'
    return expr

@as_form
class InsertOne(BaseMongo):
  insert_type: Literal['insert_one', 'insert_many'] = 'insert_one'
  data: dict
  def buildExpression(self):
    if self.data and any(self.data):
      self.data = json_to_mongo(self.data)
      expr = f'entity.{self.insert_type}({self.data})'
      return expr
    return None

@as_form
class InsertMany(BaseMongo):
  insert_type: Literal['insert_one', 'insert_many'] = 'insert_many'
  data: List[dict]
  def buildExpression(self):
    if (self.data):
      expr = f'entity.{self.insert_type}({self.data})'
      return expr
    return None

@as_form
class UpdateOne(BaseMongo):
  update_type: Literal['update_one', 'update_many'] = 'update_one'
  query: Optional[dict]
  data: dict
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    if self.data and any(self.data):
      self.data = json_to_mongo(self.data)
      expr = f'entity.{self.update_type}({self.query}, {self.data})'
      return expr
    return None

@as_form
class UpdateMany(BaseMongo):
  update_type: Literal['update_one', 'update_many'] = 'update_many'
  query: Optional[dict]
  data: dict
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    if self.data:
      expr = f'entity.{self.update_type}({self.query}, {self.data})'
      return expr
    return None

@as_form
class Update(BaseMongo):
  update_type: Literal['update_one', 'update_many'] = 'update_one'
  query: Optional[dict]
  data: dict
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    if self.data:
      expr = f'entity.{self.update_type}({self.query}, {self.data})'
      return expr
    return None

@as_form
class Delete(BaseMongo):
  delete_type: Literal['delete_one', 'delete_many'] = 'delete_one'
  query: Optional[dict]
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
      expr = f'entity.{self.delete_type}({self.query})'
      return expr
    return None

@as_form
class DeleteOne(BaseMongo):
  delete_type: Literal['delete_one', 'delete_many'] = 'delete_one'
  query: Optional[dict]
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
      expr = f'entity.{self.delete_type}({self.query})'
      return expr
    return None

@as_form
class DeleteMany(BaseMongo):
  delete_type: Literal['delete_one', 'delete_many'] = 'delete_many'
  query: Optional[dict]
  def buildExpression(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
      expr = f'entity.{self.delete_type}({self.query})'
      return expr
    return None

@as_form
class QueryResults(BaseMongo):
  query_type: Literal['find_one', 'find'] = 'find_one'
  query: Optional[dict]
  projection: Optional[dict]
  sort: Optional[dict]
  skip: Optional[int]
  items: Optional[List[Dict]] = []

'''
Bulk Write section...
'''
class BulkUpdate(BaseModel):
  bulk_type: Literal['update_one', 'update_many'] = 'update_one'
  query: dict
  data: dict
  def buildWrite(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    if self.bulk_type == 'update_many':
      result = BulkUpdateMany(self.query, self.data)
    else:
      result = BulkUpdateOne(self.query, self.data)
    return result

class BulkDelete(BaseModel):
  bulk_type: Literal['delete_one', 'delete_many'] = 'delete_one'
  query: dict
  def buildWrite(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    if self.bulk_type == 'delete_many':
      result = BulkDeleteMany(self.query)
    else:
      result = BulkDeleteOne(self.query)
    return result

class BulkReplace(BaseModel):
  bulk_type: Literal['replace_one'] = 'replace_one'
  query: dict
  data: dict
  def buildWrite(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    result = BulkReplaceOne(self.query, self.data)
    return result

class BulkInsert(BaseModel):
  bulk_type: Literal['insert_one'] = 'insert_one'
  data: dict
  def buildWrite(self):
    result = BulkInsertOne(self.data)
    return result

class BulkCount(BaseModel):
  bulk_type: Literal['bulk_count'] = 'bulk_count'
  query: Optional[dict]
  def buildWrite(self):
    if self.query and any(self.query):
      self.query = json_to_mongo(self.query)
    else:
      self.query = {}
    result = BulkInsertOne(self.data)
    return result

class BulkWrite(BaseMongo):
  batch: List[Union[BulkUpdate, BulkDelete, BulkReplace, BulkInsert]] # most specific first...
  def buildPayload(self):
    payload = []
    for x in self.batch:
      obj = x.buildWrite()
      payload.append(obj)
    return payload
'''
Aggregate Pipeline
'''
class AggregatePipeline(BaseModel):
  database: str
  aggregate: str
  pipeline: List[dict]
  cursor: dict

