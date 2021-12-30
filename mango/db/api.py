import json, os
from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)
from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson import json_util, ObjectId
from settings import (
    DATABASE_CLUSTER,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_USERNAME,
)
# from mango.auth.models import AuthHandler, Credentials
from mango.db.models import datetime_parser, json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline

uri = f'mongodb+srv://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_CLUSTER}.mongodb.net/{DATABASE_NAME}?retryWrites=true&w=majority'
client = MongoClient(uri)
db = client.test

print(uri)

# auth_handler = AuthHandler()

router = APIRouter(
  prefix = '/api',
  tags = ['Mongodon']
)

@router.post('/find')
# async def find(query: Query, user_id=Depends(auth_handler.auth_wrapper)):
async def find(query: Query):
  database = query.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = query.buildExpression()
  entity = db[query.collection]
  cursor = eval(expr)
  results = list(cursor)
  data = json.loads(json.dumps(results, default=json_from_mongo))
  return data

def find_sync(query: Query):
  database = query.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = query.buildExpression()
  entity = db[query.collection]
  cursor = eval(expr)
  results = list(cursor)
  data = json.loads(json.dumps(results, default=json_from_mongo))
  return data


@router.post('/findOne')
async def find_one(query: QueryOne):
  database = query.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = query.buildExpression()
  entity = db[query.collection]
  result = eval(expr)
  data = json.loads(json.dumps(result, default=json_from_mongo))
  return data

@router.post('/count')
async def count(query: Count):
  database = query.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = query.buildExpression()
  entity = db[query.collection]
  result = eval(expr)
  data = json.loads(json.dumps(result, default=json_from_mongo))

  return {'count': data}

@router.post('/bulkRead')
async def bulk_read(batch: List[Union[Query, QueryOne]]):
  payload = []
  for query in batch:
    database = query.database
    if not database:
      database = DATABASE_NAME
    db = client[database]
    expr = query.buildExpression()
    entity = db[query.collection]
    cursor = eval(expr)
    results = list(cursor)
    data = json.loads(json.dumps(results, default=json_from_mongo))
    payload.append(data)
  return payload

@router.post('/insertOne')
async def insert_one(payload: InsertOne):
  database = payload.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = payload.buildExpression()
  entity = db[payload.collection]
  result = eval(expr)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'inserted_id': result.inserted_id}))
  return data

@router.post('/insertMany')
async def insert_many(payload: InsertMany):
  database = payload.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = payload.buildExpression()
  entity = db[payload.collection]
  result = eval(expr)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'inserted_ids': result.inserted_ids}))
  return data

@router.post('/update')
async def update_one(payload: Update):
  database = payload.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = payload.buildExpression()
  entity = db[payload.collection]
  result = eval(expr)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'matched_count': result.matched_count, 'modified_count': result.modified_count}))
  return data

@router.post('/delete')
async def delete(payload: Delete):
  database = payload.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  expr = payload.buildExpression()
  entity = db[payload.collection]
  result = eval(expr)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'deleted_count': result.deleted_count}))
  return data

@router.post('/bulkWrite')
async def bulk_write(batch: BulkWrite):
  database = batch.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  entity = db[batch.collection]
  payload = batch.buildPayload()
  result = entity.bulk_write(payload)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'deleted_count': result.deleted_count, 'inserted_count': result.inserted_count, 'matched_count': result.matched_count, 'modified_count': result.modified_count, 'upserted_count': result.upserted_count, 'upserted_ids': result.upserted_ids}))
  return data

@router.post('/runPipeline')
async def run_pipeline(ap: AggregatePipeline):
  ap.pipeline = json.loads(json_util.dumps(ap.pipeline), object_hook=datetime_parser)
  database = ap.database
  if not database:
    database = DATABASE_NAME
  db = client[database]
  command = {"aggregate": ap.aggregate, "pipeline": ap.pipeline, "cursor": ap.cursor}
  result = db.command(command)  
  data = json.loads(json_util.dumps(result), object_hook=json_from_mongo)
  return data
