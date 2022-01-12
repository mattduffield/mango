'''
Hooks - the following are hooks allowing the FSM to send information to
        third party systems.
'''

from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from pydantic import BaseModel
from db.api import find, find_one, count, bulk_read, insert_one, insert_many, update_one, delete, bulk_write, run_pipeline
from db.models import json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
import requests
import json, os

DATABASE_NAME = os.environ.get('DATABASE_NAME')
ASANA_CLIENT_ID = os.environ.get('ASANA_CLIENT_ID')
ASANA_CLIENT_SECRET = os.environ.get('ASANA_CLIENT_SECRET')
ASANA_REDIRECT_URI = os.environ.get('ASANA_REDIRECT_URI')
ASANA_PERSONAL_ACCESS_TOKEN = os.environ.get('ASANA_PERSONAL_ACCESS_TOKEN')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_URL = os.environ.get('MAILGUN_URL')
MAILGUN_FROM_BLOCK = os.environ.get('MAILGUN_FROM_BLOCK')


class Email(BaseModel):
  from_block:Optional[str] = MAILGUN_FROM_BLOCK
  to_block:Optional[str]
  subject:str
  text:Optional[str] = None
  html:Optional[str] = None
  
  class Config:
    schema_extra = {
      "example": {
        "from_block": MAILGUN_FROM_BLOCK,
        "to_block": "matt@falm.com",
        "subject": "FALM User Request",
        "text": "Please make the new user account active!"
      }
    }

class Hook(BaseModel):
  name:str
  data:dict = {}

  class Config:
    schema_extra = {
      "name": "send_email",
      "data": {
        "from_block": MAILGUN_FROM_BLOCK,
        "to_block": "john.doe@test.com",
        "subject": "Sample Subject",
        "text": "Sample text!",
        "permission": "approve_registration"
      },
    }

async def create_user(database:str, id:str, hookData:dict, data:dict):
  data['is_active'] = False
  payload = {
    "database": database,
    "collection": "users",
    "insert_type": "insert_one",
    "data": data
  }
  query = InsertOne(**payload)
  res = await insert_one(query)
  return res

async def activate_user(database:str, id:str, hookData:dict, data:dict):
  query = {'email': data['email']}
  upd = {'$set': {'is_active': True}}
  payload = {
    "database": database,
    "collection": "users",
    "udpate_type": "update_one",
    "query": query,
    "data": upd
  }
  update = Update(**payload)
  res = await update_one(update)
  return res

async def update_password(database:str, id:str, hookData:dict, data:dict):
  query = {'email': data['email']}
  upd = {'$set': {'password': data['password']}}
  payload = {
    "database": database,
    "collection": "users",
    "udpate_type": "update_one",
    "query": query,
    "data": upd
  }
  update = Update(**payload)
  res = await update_one(update)
  return res

async def send_email(database:str, id:str, hookData:dict, data:dict):
  email = Email(**hookData)
  permission = hookData.get('permission', '')

  if email.from_block:
    from_block = email.from_block
  else:
    from_block = MAILGUN_FROM_BLOCK

  if email.to_block:
    to_block = eval('f"""' + email.to_block + '"""')
  else:
    # Need to find all emails based on permission
    payload = {
      "database": database,
      "collection": "users",
      "query_type": "find",
      "projection": {"email": 1},
      "query": {
        "$or": [          
          {"roles": {"$in": [permission]}},
          {"actions": {"$in": [permission]}}
        ]
      }
    }
    query = Query(**payload)
    res = await find(query)
    lst = [x['email'] for x in res]
    to_block = ','.join(lst)

  if email.subject:
    try:
      subject = eval('f"""' + email.subject + '"""')
    except (ValueError, SyntaxError):
      subject = email.subject
      pass
  
  if email.text:
    try:
      text = eval('f"""' + email.text + '"""')
    except (RuntimeError, TypeError, NameError, ValueError, SyntaxError) as err:
      text = email.text
      pass

  if email.html:
    try:
      html = eval('f"""' + email.html + '"""')
    except Exception as err:
      html = email.html
      print(err)
      pass

  if email.html:
    return requests.post(
      MAILGUN_URL,
      auth=("api", MAILGUN_API_KEY),
      data={"from": f"{from_block}",
            "to": [f"{to_block}"],
            "subject": f"{subject}",
            "html": f"{html}"})
  else:
    return requests.post(
      MAILGUN_URL,
      auth=("api", MAILGUN_API_KEY),
      data={"from": f"{from_block}",
            "to": [f"{to_block}"],
            "subject": f"{subject}",
            "text": f"{text}"})
