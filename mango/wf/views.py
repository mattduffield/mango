'''
WorkFlow - the following are endpoints for executing workflows.
'''
import json, os
from bson import json_util, ObjectId
from fastapi import APIRouter, HTTPException, Request, Form, Body, Query, status
from fastapi.responses import RedirectResponse
from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from mango.db.api import find, find_one, count, bulk_read, insert_one, insert_many, update_one, delete, bulk_write, run_pipeline
from mango.wf.models import User, Workflow, WorkflowRequest, WorkflowRun, WorkflowTrigger, Machine
from mango.db.models import json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
from settings import manager, templates


DATABASE_NAME = os.environ.get('DATABASE_NAME')

router = APIRouter(
  prefix = '/wf',
  tags = ['WorkFlow']
)

async def get_workflow_by_name(database:str, name:str):
  payload = {
    "database": database,
    "collection": "workflows",
    "query_type": "find_one",
    "query": {"name": name},
    "skip": 0
  }
  query = QueryOne(**payload)
  res = await find_one(query)
  return res

async def get_workflow_run_by_id(database:str, id:str):
  payload = {
    "database": database,
    "collection": "workflow-runs",
    "query_type": "find_one",
    "query": {"_id": id},
    "skip": 0
  }
  query = QueryOne(**payload)
  res = await find_one(query)
  return res

async def insert_workflow_run(database:str, run:dict, data:dict):
  wfr = WorkflowRun(**run)
  wfr.data = data
  payload = {
    "database": database,
    "collection": "workflow-runs",
    "insert_type": "insert_one",
    "data": wfr.dict()
  }
  insertOne = InsertOne(**payload)
  insert_res = await insert_one(insertOne)
  inserted_id = insert_res['inserted_id']['$oid']
  wfr.id = inserted_id
  return wfr, inserted_id

async def update_workflow_run_state_by_id(database:str, id:str, state:str):
  payload = {
    "database": database,
    "collection": "workflow-runs",
    "update_type": "update_one",
    "query": {"_id": id},
    "data": {"$set": {"current_state": state}}
  }
  updateOne = Update(**payload)
  res = await update_one(updateOne)
  return res

async def init_workflow_run(req:WorkflowRequest):
  if not req.database:
    req.database = DATABASE_NAME

  # 1. Load workflow for UserSignup
  wf_res = await get_workflow_by_name(database=req.database, name=req.name)

  # 2. Insert a new record into workflow-runs
  wfr, inserted_id = await insert_workflow_run(database=req.database, run=wf_res, data=req.data)

  # 3. Run Machine
  machine = Machine(workflow_run=wfr, database=req.database)
  try:
    run_state, redirect_url = await machine.next(database=req.database, trigger=req.trigger)
  except Exception as err:
    print('Machine error...')
    print(err)
    raise HTTPException(status_code=404, detail=err.args)

  # 4. Update WorkflowRun
  update_res = await update_workflow_run_state_by_id(database=req.database, id=inserted_id, state=run_state.current_state)
  return update_res

async def trigger_workflow_run_by_id(req:WorkflowTrigger):
  if not req.database:
    req.database = DATABASE_NAME

  # 1. Load workflow-run
  wfr_res = await get_workflow_run_by_id(database=req.database, id=req.id)
  wfr = WorkflowRun(**wfr_res)
  wfr.id = req.id
  if req.trigger_data:
    wfr.data = {**wfr.data, **req.trigger_data}

  # 2. Run Machine
  machine = Machine(workflow_run=wfr, database=req.database)
  try:
    run_state, redirect_url = await machine.next(database=req.database, trigger=req.trigger)
  except Exception as err:
    raise HTTPException(status_code=404, detail=err.args)
  
  # 3. Update WorkflowRun
  update_res = await update_workflow_run_state_by_id(database=req.database, id=req.id, state=run_state.current_state)
  return update_res, redirect_url

@router.post('/init-workflow-run')
async def init_workflow_run_as_body(payload:WorkflowRequest):
  '''
    {
      "database": "<database>",
      "workflow_name": "UserSignup",
      "trigger": "signup",
      "data": {"username": "Matt", "email": "mattd@pegramins.com", "password": "wordpass1"},
    }
  '''
  # res = await init_workflow_run(workflow_name=workflow_name, trigger=trigger, data=data, user=user)
  res = await init_workflow_run(payload)
  return res

@router.post('/trigger-workflow-run')
async def trigger_workflow_run_as_body(req:WorkflowTrigger):
# async def trigger_workflow_run_as_body(workflow_run_id:str = Body(None), trigger:Optional[str] = Body(None), user: Optional[User] = Body(None)):
  '''
      {
        "database": "<database>",
        "workflow_run_id": "60b55c9fe2e8d57cde9572c7",
        "trigger": "approve",
        "trigger_data": "..."
      }
    '''
  res, redirect_url = await trigger_workflow_run_by_id(req)
  return res

@router.post('/trigger-workflow-run-as-form')
async def trigger_workflow_run_as_form(request:Request, database:str = Form(...), id:str = Form(...), trigger:Optional[str] = Form(None)):
  '''
    {
      "database": "<database>",
      "id": "60b55c9fe2e8d57cde9572c7",
      "trigger": "approve"
    }
  '''
  form = await request.form()
  # new_dict = {'database': database, 'id': id, 'trigger': trigger, **form}
  trigger_data = {k:v for (k,v) in form.items() if k != 'database' and k != 'id' and k != 'trigger'}
  payload = {
    "database": database,
    "id": id,
    "trigger": trigger,
    "trigger_data": trigger_data
  }
  req = WorkflowTrigger(**payload)
  res, redirect_url = await trigger_workflow_run_by_id(req)
  if redirect_url:
    resp = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    return resp

  return res
