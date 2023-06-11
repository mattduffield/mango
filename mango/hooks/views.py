from pathlib import Path
import json, os
import requests
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.payment import Payment
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.attachable import Attachable, AttachableRef
# import asana

from mango.db.api import find, find_one, count, bulk_read, insert_one, insert_many, update_one, delete, bulk_write, run_pipeline
from mango.db.models import json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
from mango.wf.models import WorkflowRun
from mango.template_utils.utils import configure_templates


DATABASE_NAME = os.environ.get('DATABASE_NAME')
TEMPLATE_DIRECTORY = os.environ.get('TEMPLATE_DIRECTORY')
ASANA_CLIENT_ID = os.environ.get('ASANA_CLIENT_ID')
ASANA_CLIENT_SECRET = os.environ.get('ASANA_CLIENT_SECRET')
ASANA_REDIRECT_URI = os.environ.get('ASANA_REDIRECT_URI')
ASANA_PERSONAL_ACCESS_TOKEN = os.environ.get('ASANA_PERSONAL_ACCESS_TOKEN')

templates = configure_templates(directory=TEMPLATE_DIRECTORY)

router = APIRouter(
  prefix = '/hooks',
  tags = ['Hooks']
)

async def get_pipeline_resources(database: str, workflow_run_id: str):
  pipeline = [
    { 
      '$match': {
        '$expr': { '$eq': [ '$is_default', True ] }
      },
    },
    { 
      '$lookup': {
        'from': 'organization',
        'pipeline': [
          { 
            '$match': { 
              '$expr': { '$eq': [ '$is_default', True ] }
            }
          }
        ],
        'as': 'current_organization'
      }
    },
    { '$unwind': '$current_organization' },
    { 
      '$lookup': {
        'let': {'wfr_id': { '$toObjectId': workflow_run_id }},
        'from': 'workflow_run',
        'pipeline': [
          { 
            '$match': { 
              '$expr': { '$eq': [ '$_id', '$$wfr_id' ] }
            }
          }
        ],
        'as': 'workflow_run'
      }
    },
    { '$unwind': '$workflow_run' }
  ]

  ap = AggregatePipeline(
    database=database,
    aggregate='xtra',
    pipeline=pipeline,
    cursor={},
  )
  pipeline_result = await run_pipeline(ap)
  result = pipeline_result['cursor']['firstBatch']
  return result

@router.get('/approve-user/{database}/{workflow_run_id}', response_class=HTMLResponse)
async def approve_user(request: Request, database: str, workflow_run_id: str):
  if not database:
    database = DATABASE_NAME
  [res] = await get_pipeline_resources(database=database, workflow_run_id=workflow_run_id)
  current_organization = res.get('current_organization', None)
  workflow_run = res.get('workflow_run', None)
  view = {
    "lookups": {
      "current_organization": current_organization
    },
    "workflow_run": workflow_run
  }
  wfr = WorkflowRun(**view['workflow_run'])
  return templates.TemplateResponse('hooks/approve_user.html', {'request': request, 'database': database, 'id': workflow_run_id, 'wfr': wfr, 'view': view})

@router.get('/reset-password/{database}/{workflow_run_id}', response_class=HTMLResponse)
async def reset_password(request: Request, database: str, workflow_run_id: str):
  if not database:
    database = DATABASE_NAME
  view = {}
  [res] = await get_pipeline_resources(database=database, workflow_run_id=workflow_run_id)
  current_organization = res.get('current_organization', None)
  workflow_run = res.get('workflow_run', None)
  view = {
    "lookups": {
      "current_organization": current_organization
    },
    "workflow_run": workflow_run
  }
  wfr = WorkflowRun(**view['workflow_run'])
  return templates.TemplateResponse('hooks/reset_password.html', {'request': request, 'database': database, 'id': workflow_run_id, 'wfr': wfr, 'view': view})

@router.get('/asana/callback', response_class=HTMLResponse)
async def asana_callback(request: Request):
  print('Inside Asana callback...')

@router.get('/asana/test', response_class=HTMLResponse)
async def asana_test(request: Request):
  BACKLOG = '1200235773024123'
  CURRENT_SPRINT = '1200235773024138'
  IN_PROGRESS = '1200235773024139'
  IN_QA = '1200235773024140'
  TESTED_IN_QA = '1200236387365023'
  IN_UAT = '1200235773024141'
  APPROVED_IN_UAT = '1200248413997612'
  IN_PRODUCTION = '1200235773024142'

  # Construct an Asana client
  # client = asana.Client.access_token(ASANA_PERSONAL_ACCESS_TOKEN)
  # Set things up to send the name of this script to us to show that you succeeded! This is optional.
  # client.options['client_name'] = "hello_world_python"

  # Get Workspaces
  # workspaces = client.workspaces.get_workspaces()
  # for ws in workspaces:
  #   print(ws)

  # Get a Task
  # task = client.tasks.get_task('1201013989650375')
  # print(task)

  # Get Tasks for a given Project
  # tasks = client.tasks.get_tasks_for_project('1200235773024122')
  # for task in tasks:
  #   print(task)

  # Get Sections for a given Project
  # sections = client.sections.get_sections_for_project('1200235773024122')
  # for section in sections:
  #   print(section)

  # Get Tasks for a given Section
  # tasks = client.tasks.get_tasks_for_section(BACKLOG)
  # for task in tasks:
  #   print(task)

  # ws = client.workspaces.get_workspaces()
  # print(ws)

  # project_id = '1200235773024122'
  # section = asana_create_section(project_id=project_id, section_name='New Test Section')

  workspace = '333506893445312'
  project_id = '1200235773024122'
  task = asana_create_task(workspace=workspace, project_id=project_id, task_name='Malerie get to work!!')
  print(task)
  task_id = task['data']['gid']
  # task_id = '1201034344893639'
  attachment_url = 'https://storage.googleapis.com/q1-server-staging.appspot.com/prospect-quotes/runs/60c27045c2ef5d000ae4427e/602c58cc81198909d5fd79c7/1632240742041/step_9.png'
  attachment = asana_upload_task_attachment(task_id=task_id, attachment_name='Task Image', attachment_url=attachment_url)
  print(attachment)
  attachment_id = attachment['data']['gid']

def asana_post(url:str, data:dict):
  # project_id = '1200235773024122'
  # url = f'https://app.asana.com/api/1.0/projects/{project_id}/sections'
  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {ASANA_PERSONAL_ACCESS_TOKEN}"
  }
  response = requests.post(url, json=data, headers=headers).json()
  print(response)
  return response

def asana_create_section(project_id:str, section_name:str):
  url = f"https://app.asana.com/api/1.0/projects/{project_id}/sections"
  data = {
    "data": {
      "name": f"{section_name}"
    }
  }
  response = asana_post(url, data=data)
  return response

def asana_create_task(workspace:str, project_id:str, task_name:str):
  url = f"https://app.asana.com/api/1.0/tasks"
  data = {
    "data": {
      "name": f"{task_name}",
      "projects": [
        f"{project_id}"
      ],
      "resource_subtype": "default_task",
      "workspace": f"{workspace}"
    }
  }
  response = asana_post(url, data=data)
  return response

def asana_upload_task_attachment(task_id:str, attachment_name:str, attachment_url:str):
  url = f"https://app.asana.com/api/1.0/tasks/{task_id}/attachments"
  data = {
    "data": {
      "name": f"{attachment_name}",
      "resource_subtype": "external",
      "url": attachment_url
    }
  }
  response = asana_post(url, data=data)
  return response


# Create a Task in a project
'''
curl -X POST https://app.asana.com/api/1.0/tasks \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer 1/354936440630751:0de752e7e10a5defe6a9fab31af8c36a' \
  -d '{"data": {"name":"Test Task From System","projects":["1200235773024122"],"resource_subtype": "default_task","workspace": "333506893445312"} }'
'''

# Upload an Attachment to a Task
'''
curl -X POST https://app.asana.com/api/1.0/tasks/{task_gid}/attachments \
  -H 'Content-Type: multipart/form-data' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}' \
  -d '{"data": {"field":"value","field":"value"} }'
  '''

# Create a Section in a Project
'''
curl -X POST https://app.asana.com/api/1.0/projects/1200235773024122/sections \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer 1/354936440630751:0de752e7e10a5defe6a9fab31af8c36a' \
  -d '{"data": {"name":"test section"} }'
'''
