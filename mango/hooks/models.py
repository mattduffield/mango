'''
Hooks - the following are hooks allowing the FSM to send information to
        third party systems.
'''

import requests
import json, os
from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from pydantic import BaseModel
from mango.db.api import find, find_one, count, bulk_read, insert_one, insert_many, update_one, delete, bulk_write, run_pipeline
from mango.db.models import json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline

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
  cc_block:Optional[str]
  subject:str
  text:Optional[str] = None
  html:Optional[str] = None
  
  class Config:
    schema_extra = {
      "example": {
        "from_block": MAILGUN_FROM_BLOCK,
        "to_block": "matt@falm.com",
        "cc_block": "matt@falm.com",
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
        "cc_block": "matt@falm.com",
        "subject": "Sample Subject",
        "text": "Sample text!",
        "permission": "approve_registration"
      },
    }
