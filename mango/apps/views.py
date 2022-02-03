from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from typing import (
  Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)
from fastapi_router_controller import Controller
from mango.core.views import (
  CreateView,
  UpdateView,
  DeleteView, 
  ListView, 
  get_controller,
  GenericListView,
)
from mango.auth.models import Credentials
from mango.db.models import datetime_parser, json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
from mango.db.api import find, find_one
from mango.apps.forms import AppForm, FieldForm
from mango.apps.models import App, Field
from settings import manager, templates, DATABASE_NAME

create_controller = get_controller()
update_controller = get_controller()
delete_controller = get_controller()
list_controller = get_controller()


edit_button = '''
<a hx-get="apps/{{object._id}}"
  hx-target="#viewport"
  hx-swap="innerHTML"
  hx-push-url="true"
  hx-indicator="#content-loader"
  class="cursor-pointer"
  >
  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" 
    fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
  </svg>
</a>
'''
delete_button = '''
<a hx-get="apps/{{object._id}}/delete"
  hx-target="#viewport"
  hx-swap="innerHTML"
  hx-push-url="true"
  hx-indicator="#content-loader"
  class="cursor-pointer"
  >
  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" 
    fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
</a>
'''

@create_controller.resource()
class AppCreateView(CreateView):
  form_class = AppForm
  model_class = App
  object_display = lambda self, object: f'New'

  @create_controller.route.get('/apps/create', response_class=HTMLResponse, name='app-create')
  async def get(self, request: Request, user=Depends(manager)):
    return await super().get(request=request)

  @create_controller.route.post('/apps/create', response_class=HTMLResponse, name='app-create')
  async def post(self, request: Request, user=Depends(manager)):
    return await super().post(request=request)


@update_controller.resource()
class AppUpdateView(UpdateView):
  form_class = AppForm
  model_class = App
  object_display = lambda self, object: f'''{object['name']}'''

  @update_controller.route.get('/apps/{_id}', response_class=HTMLResponse, name='app-item')
  async def get(self, request: Request, _id: str, user=Depends(manager)):
    return await super().get(request=request, _id=_id)

  @update_controller.route.post('/apps/{_id}', response_class=HTMLResponse, name='app-item')
  async def post(self, request: Request, _id: str, user=Depends(manager)):
    return await super().post(request=request, _id=_id)


@delete_controller.resource()
class AppDeleteView(DeleteView):
  model_class = App
  object_display = lambda self, object: f'''{object['name']}'''

  @delete_controller.route.get('/apps/{_id}/delete', response_class=HTMLResponse, name='app-delete')
  async def get(self, request: Request, _id: str, user=Depends(manager)):
    return await super().get(request=request, _id=_id)

  @delete_controller.route.post('/apps/{_id}/delete', response_class=HTMLResponse, name='app-delete')
  async def post(self, request: Request, _id: str, user=Depends(manager)):
    return await super().post(request=request, _id=_id)


@list_controller.resource()
class AppListView(ListView):
  model_class = App
  # create_url = 'entity-list'
  delete_url = lambda self, object: f''

  @list_controller.route.get('/apps', response_class=HTMLResponse, name='app-list')
  async def get(self, request: Request, search: Optional[str] = '', user=Depends(manager)):
    return await super().get(request=request, search=search)

  def get_table_definition(self, context):
    context['table_header'] = [
      {
        'name': 'Name', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'Name Plural', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'List URL', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'List Route Name', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'status', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'html': '<span class="sr-only">Actions</span>', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
    ]
    context['table_body'] = [
      {
        'name': 'name',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'name': 'name_plural',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'name': 'list_url',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'name': 'list_route_name',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'html': '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'actions': [
          edit_button,
          delete_button,
        ],
        'class': 'flex justify-between px-6 py-4 whitespace-nowrap text-right text-sm font-medium',
      },
    ]



field_create_controller = get_controller()
field_update_controller = get_controller()
field_delete_controller = get_controller()
field_list_controller = get_controller()

@field_update_controller.resource()
class FieldUpdateView(UpdateView):
  form_class = FieldForm
  model_class = Field
  object_display = lambda self, object: f'{object["name"]}'

  @update_controller.route.get('/apps/{_id}/fields', response_class=HTMLResponse, name='field-item')
  async def get(self, request: Request, _id: str, user=Depends(manager)):
    return await super().get(request=request, _id=_id)

  @update_controller.route.post('/apps/{_id}/fields', response_class=HTMLResponse, name='field-item')
  async def post(self, request: Request, _id: str, user=Depends(manager)):
    return await super().post(request=request, _id=_id)
