'''
QuickBooks - the following are endpoints for supporting managing data to and from QuickBooks.

https://github.com/IntuitDeveloper/SampleOAuth2_UsingPythonClient
https://github.com/ej2/python-quickbooks
https://pypi.org/project/python-quickbooks/
https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0#refresh-the-token
https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api/data-queries
https://developer.intuit.com/app/developer/qbo/docs/workflows/manage-linked-transactions
https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice
https://towardsdatascience.com/how-to-integrate-quickbooks-with-python-8be2d69f96cb
'''

from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from mango.db.api import find, find_one, count, bulk_read, insert_one, insert_many, update_one, delete, bulk_write, run_pipeline
from mango.wf.models import User, Workflow, WorkflowRequest, WorkflowRun, WorkflowTrigger, Machine
from mango.qb.models import QueryModel, CreateModel, UpdateModel, NewAttachment, NewNoteAttachment
from mango.db.models import json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
from fastapi import APIRouter, HTTPException, Request, Form, Body, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from quickbooks import QuickBooks
from quickbooks.cdc import change_data_capture
from quickbooks.objects.customer import Customer
from quickbooks.objects.payment import Payment
from quickbooks.objects.preferences import Preferences
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.vendor import Vendor
from quickbooks.objects.item import Item
from quickbooks.objects.attachable import Attachable, AttachableRef

from bson import json_util, ObjectId
import datetime
import json
import os
import requests

DATABASE_NAME = os.environ.get('DATABASE_NAME')
QUICKBOOKS_CLIENT_ID = os.environ.get('QUICKBOOKS_CLIENT_ID')
QUICKBOOKS_CLIENT_SECRET = os.environ.get('QUICKBOOKS_CLIENT_SECRET')
QUICKBOOKS_REDIRECT_URI = os.environ.get('QUICKBOOKS_REDIRECT_URI')
QUICKBOOKS_WEBHOOKS_VERIFIER_TOKEN = os.environ.get('QUICKBOOKS_WEBHOOKS_VERIFIER_TOKEN')
QUICKBOOKS_ENVIRONMENT = os.environ.get('QUICKBOOKS_ENVIRONMENT')
QBO_BASE_SANDBOX = os.environ.get('QBO_BASE_SANDBOX')
QBO_BASE_PROD = os.environ.get('QBO_BASE_PROD')

router = APIRouter(
  prefix = '/qb',
  tags = ['QuickBooks']
)

templates = Jinja2Templates(directory="templates")

def quickbooks_get_auth_client():
  auth_client = AuthClient(
    client_id=QUICKBOOKS_CLIENT_ID,
    client_secret=QUICKBOOKS_CLIENT_SECRET,
    environment=QUICKBOOKS_ENVIRONMENT,
    redirect_uri=QUICKBOOKS_REDIRECT_URI,
  )
  return auth_client

def quickbooks_get_full_auth_client(request:Request):
  auth_client = quickbooks_get_auth_client()
  auth_client.access_token = request.session.get('access_token', None)
  auth_client.refresh_token = request.session.get('refresh_token', None)
  auth_client.realm_id = request.session.get('realm_id', None)
  return auth_client

def quickbooks_get_auth_url():
  auth_client = quickbooks_get_auth_client()
  scopes = [
    Scopes.ACCOUNTING,
  ]
  auth_url = auth_client.get_authorization_url(scopes)
  state_token = auth_client.state_token
  return {"auth_url": auth_url, "state_token": state_token}

def quickbooks_get_tokens(auth_code:str, realm_id:str):
  auth_client = quickbooks_get_auth_client()
  auth_client.get_bearer_token(auth_code, realm_id=realm_id)
  return {
    "access_token": auth_client.access_token, 
    "refresh_token": auth_client.refresh_token,
    "id_token": auth_client.id_token
  }

def quickbooks_revoke(refresh_token:str):
  auth_client = quickbooks_get_auth_client()
  auth_client.revoke(token=refresh_token)

def quickbooks_get_entity(entity_name:str):
  lookup = {
    'Customer': Customer,
    'Invoice': Invoice,
    'Payment': Payment,
    'Preferences': Preferences,
    'Vendor': Vendor,
  }
  return lookup[entity_name]

def eval_dict(data:dict, **kwargs):
  for key, value in kwargs.items():
    if type(value) == str and '{' in value and '}' in value:
      kwargs[key] = eval('f"""' + value + '"""')

  return kwargs

def set_entity(entity, **kwargs):
  for key, value in kwargs.items():
    setattr(entity, key, value)

def quickbooks_execute(entity, query:QueryModel, client:QuickBooks, data:dict = None):
  result = None

  if query.get:
    result = entity.get(query.get, qb=client)
  elif query.filter:
    compiled_dict = eval_dict(data, **query.filter)
    result = entity.filter(**compiled_dict, qb=client)
  elif query.all:
    compiled_dict = eval_dict(data, **query.all)
    result = entity.all(**compiled_dict, qb=client)
  elif query.where:
    compiled_dict = eval_dict(data, **query.where)
    result = entity.where(**compiled_dict, qb=client)
  elif query.query:
    result = entity.query(query.query, qb=client)
  elif query.count:
    result = entity.count(query.count, qb=client)

  return result

def quickbooks_get(request: Request, query: QueryModel):
  headers = { 
    'Accept': "application/json"
  }
  meta_version = '/v3/company'
  # base_url = f'https://sandbox-quickbooks.api.intuit.com{meta_version}'
  base_url = f'https://quickbooks.api.intuit.com{meta_version}'
  url = f"{base_url}/{request.session['realm_id']}/query?query={query.query}&minorversion=62"
  print(url)
  headers['Authorization'] = f"Bearer {request.session['access_token']}"
  resp = requests.get(url, headers=headers)
  # print(headers)
  print(resp.content)
  resp_object = json.loads(resp.content)
  return resp_object['QueryResponse']


@router.get('/authorize')
def quickbooks_authorize(request: Request):
  auth_response = quickbooks_get_auth_url()
  url = auth_response["auth_url"]
  request.session['state'] = auth_response["state_token"]

  response = RedirectResponse(url=url)
  return response

@router.get('/revoke')
def quickbooks_revoke(request: Request):
  token = request.session['refresh_token']
  quickbooks_revoke(token)

@router.get('/callback')
async def quickbooks_callback(request: Request):
  auth_client = quickbooks_get_auth_client()
  auth_client.state_token = request.session.get('state', None)

  state_tok = request.query_params.get('state', None)
  error = request.query_params.get('error', None)
  
  if error == 'access_denied':
    # return redirect('app:index')
    raise HTTPException(status_code=401, detail='Access denied!')
  
  if state_tok is None:
    raise HTTPException(status_code=404, detail='Invalid token!')
  elif state_tok != auth_client.state_token:  
    raise HTTPException(status_code=401, detail='Unauthorized')
  
  auth_code = request.query_params.get('code', None)
  realm_id = request.query_params.get('realmId', None)
  request.session['realm_id'] = realm_id

  if auth_code is None:
    raise HTTPException(status_code=404, detail='Missing authorization!')

  try:
    tokens_response = quickbooks_get_tokens(auth_code=auth_code, realm_id=realm_id)
    request.session['access_token'] = tokens_response["access_token"]
    request.session['refresh_token'] = tokens_response["refresh_token"]
    request.session['id_token'] = tokens_response["id_token"]
  except AuthClientError as e:
    # just printing status_code here but it can be used for retry workflows, etc
    print(e.status_code)
    print(e.content)
    print(e.intuit_tid)
  except Exception as e:
    print(e)
  # return redirect('app:connected')
  return {"status": "OK"}

@router.post('/query')
async def quickbooks_query(request: Request, query: QueryModel):
  '''
    Refer: https://pypi.org/project/python-quickbooks/
    \n
    {
      "entity_name": "Customer",
      "get": "5"
    }
    \n
    {
      "entity_name": "Payment",
      "filter": {"CustomerRef": "3", "max_results": 2}
    }
    \n
    {
      "entity_name": "Customer",
      "all": {"order_by": "CompanyName DESC", "max_results": 3}
    }
    \n
    {
      "entity_name": "Customer",
      "where": {"where_clause": "CompanyName LIKE 'S%'", "order_by": "CompanyName DESC", "max_results": 2}
    }
    \n
    {
      "entity_name": "Customer",
      "query": "SELECT * FROM Customer WHERE CompanyName LIKE 'Am%'"
    }
    \n
    {
      "entity_name": "Customer",
      "count": "CompanyName LIKE 'AMY%'"
    }
    \n
  '''
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()
  
  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )

  entity = quickbooks_get_entity(query.entity_name)
  result = quickbooks_execute(entity, query, client)
  return result

@router.post('/select')
async def quickbooks_query(request: Request, query: QueryModel):
  '''
    Refer: https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer
    \n
    { "entity_name": "Invoice", "query": "SELECT * FROM Invoice" }
    \n
    { "entity_name": "Invoice", "query": "SELECT * FROM Invoice WHERE Id = '96062'" }
    \n
  '''
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()
  
  return quickbooks_get(request, query)

@router.post('/run_batch')
async def quickbooks_run_batch(request: Request, batch: List[QueryModel]):
  '''
    Refer: https://pypi.org/project/python-quickbooks/
    \n
    [
      \n
      {
        "entity_name": "Customer",
        "get": "5"
      },
      \n
      {
        "entity_name": "Invoice",
        "filter": {"CustomerRef": "{data['Customer'].Id}", "order_by": "TxnDate"}
      },
      \n
      {
        "entity_name": "Payment",
        "where": {"where_clause": "CustomerRef = '{data['Customer'].Id}'", "order_by": "TxnDate"}
      }
      \n
    ]
  '''

  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()
  
  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )
  
  data = {}
  for query in batch:
    entity = quickbooks_get_entity(query.entity_name)
    entity_result = quickbooks_execute(entity, query, client, data)
    data[query.entity_name] = entity_result
  return data

@router.post('/create')
async def quickbooks_query(request: Request, create: CreateModel):
  '''
    Refer: https://pypi.org/project/python-quickbooks/
    \n
    {
      "entity_name": "Customer",
      "data": {
        "CompanyName": "TEST CUSTOMER",
        "DisplayName": "TEST CUSTOMER"
      }
    }
    \n
  '''
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()
  
  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )

  entity_type = quickbooks_get_entity(create.entity_name)
  entity = entity_type()
  set_entity(entity, **create.data)
  # entity = entity.from_json(create.data)
  entity.save(qb=client)
  
  return {"status": "OK"}

@router.post('/update')
async def quickbooks_update(request: Request, update: UpdateModel):
  '''
    Refer: https://pypi.org/project/python-quickbooks/
    \n
    {
      "entity_name": "Customer",
      "entity_id": "59",
      "data": {
        "GivenName": "Matthew",
        "FamilyName": "Duffield",
        "PrimaryEmailAddr": {
          "Address": "matt@falm.com"
        }
      }
    }
    \n
  '''
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()
  
  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )

  entity_type = quickbooks_get_entity(update.entity_name)
  entity = entity_type.get(update.entity_id, qb=client)
  set_entity(entity, **update.data)
  entity.save(qb=client)
  
  return {"status": "OK"}

@router.post('/add_note_attachment')
async def quickbooks_company_info(request: Request, new_note: NewNoteAttachment):
  '''
    Refer: https://pypi.org/project/python-quickbooks/
    \n
    {
      "entity_name": "Customer",
      "entity_id": "5",
      "note": "Called and confirmed address information."
    }
    \n
  '''
  
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()

  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )

  entity = quickbooks_get_entity(new_note.entity_name)
  entity_object = entity.get(new_note.entity_id, qb=client)

  attachment = Attachable()
  attachable_ref = AttachableRef()
  attachable_ref.EntityRef = entity_object.to_ref()
  attachment.AttachableRef.append(attachable_ref)
  attachment.Note = new_note.note
  attachment.save(qb=client)

  return {"status": "OK"}

@router.post('/add_attachment')
async def quickbooks_add_attachment(request: Request, new_attachment: NewAttachment):
  '''
    Refer: https://pypi.org/project/python-quickbooks/
    \n
    {
      "entity_name": "Customer",
      "entity_id": "5"
    }
    \n
  '''
  
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()

  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )

  entity = quickbooks_get_entity(new_attachment.entity_name)
  entity_object = entity.get(new_attachment.entity_id, qb=client)

  file_path = f'{os.getcwd()}/static/assets/User Guide 2021.pdf'
  print(os.getcwd())
  print(file_path)
  attachment = Attachable()
  attachable_ref = AttachableRef()
  attachable_ref.EntityRef = entity_object.to_ref()
  attachment.AttachableRef.append(attachable_ref)
  attachment.FileName = 'User Guild 2021.pdf'
  attachment._FilePath = file_path
  attachment.ContentType = 'application/pdf'
  attachment.save(qb=client)

  return {"status": "OK"}

@router.post('/webhooks')
async def quickbooks_webhooks(request: Request):
  data = await request.json()
  record = InsertOne(
    database=DATABASE_NAME,
    collection='qb_webhook',
    data=data
  )
  resp = await insert_one(record)
  return { 'webhooks': 'received'}

@router.get('/cdc')
async def quickbooks_change_data_capture(request: Request, changed_since: str):
  changed_since_date = datetime.datetime.strptime(changed_since, '%Y-%m-%d')
  auth_client = quickbooks_get_full_auth_client(request)
  auth_client.refresh()
  
  client = QuickBooks(
    auth_client=auth_client,
    refresh_token=auth_client.refresh_token,
    company_id=auth_client.realm_id,
  )

  cdc_response = change_data_capture([Customer, Vendor, Item, Invoice], changed_since_date, qb=client)
  response = {
    'changed_since_date': changed_since_date,
    'customer': [],
    'vendor': [],
    'item': [],
    'invoice': [],
  }
  if hasattr(cdc_response, 'Customer'):
    for customer in cdc_response.Customer:
      # map changes to update...
      response['customer'].append({ 'Id': customer.Id, 'CompanyName': customer.CompanyName })
      print(customer)
  if hasattr(cdc_response, 'Vendor'):
    for vendor in cdc_response.Vendor:
      # map changes to update...
      response['vendor'].append({ 'Id': vendor.Id, 'CompanyName': vendor.CompanyName })
      print(vendor)
  if hasattr(cdc_response, 'Item'):
    for item in cdc_response.Item:
      # map changes to update...
      response['item'].append({ 'Id': item.Id, 'Name': item.Name })
      print(item)
  if hasattr(cdc_response, 'Invoice'):
    for invoice in cdc_response.Invoice:
      # map changes to update...
      print(invoice)
  
  return response
