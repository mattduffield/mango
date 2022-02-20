from http.client import HTTPException
from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from typing import (
  Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)
from fastapi_router_controller import Controller
from mango.core.models import AppRelated
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
from mango.app_fields.forms import AppFieldForm
from mango.app_fields.models import AppField
from settings import manager, templates, DATABASE_NAME

create_controller = get_controller()
update_controller = get_controller()
delete_controller = get_controller()
list_controller = get_controller()


edit_button = '''
<a hx-get="app_fields/{{object._id}}"
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
<a hx-get="app_fields/{{object._id}}/delete"
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
class AppFieldCreateView(CreateView):
  form_class = AppFieldForm
  model_class = AppField
  object_display = lambda self, object: f'New'
  related_fields = []

  @create_controller.route.get('/app_fields/create', response_class=HTMLResponse, name='app_fields-create')
  async def get(self, request: Request, redirect_url: str='', user=Depends(manager)):
    is_modal = False
    if redirect_url:
      is_modal = True
      self.redirect_url = redirect_url

    return await super().get(request=request, is_modal=is_modal)

  @create_controller.route.post('/app_fields/create', response_class=HTMLResponse, name='app_fields-create')
  async def post(self, request: Request, redirect_url: str='', user=Depends(manager)):
    self.redirect_url = redirect_url.replace('__', '/')
    return await super().post(request=request)


@update_controller.resource()
class AppFieldUpdateView(UpdateView):
  form_class = AppFieldForm
  model_class = AppField
  object_display = lambda self, object: f'{object["name"]}'
  related_fields = []

  @update_controller.route.get('/app_fields/{_id}', response_class=HTMLResponse, name='app_fields-item')
  async def get(self, request: Request, _id: str, redirect_url: str='', user=Depends(manager)):
    is_modal = False
    if redirect_url:
      is_modal = True
      self.redirect_url = redirect_url

    return await super().get(request=request, _id=_id, is_modal=is_modal)

  @update_controller.route.post('/app_fields/{_id}', response_class=HTMLResponse, name='app_fields-item')
  async def post(self, request: Request, _id: str, redirect_url: str='', user=Depends(manager)):
    self.redirect_url = redirect_url.replace('__', '/')
    return await super().post(request=request, _id=_id)


@delete_controller.resource()
class AppFieldDeleteView(DeleteView):
  model_class = AppField
  object_display = lambda self, object: f'''{object['name']}'''

  @delete_controller.route.get('/app_fields/{_id}/delete', response_class=HTMLResponse, name='app_fields-delete')
  async def get(self, request: Request, _id: str, redirect_url: str='', user=Depends(manager)):
    is_modal = False
    if redirect_url:
      is_modal = True
      self.redirect_url = redirect_url

    return await super().get(request=request, _id=_id, is_modal=is_modal)

  @delete_controller.route.post('/app_fields/{_id}/delete', response_class=HTMLResponse, name='app_fields-delete')
  async def post(self, request: Request, _id: str, redirect_url: str='', user=Depends(manager)):
    self.redirect_url = redirect_url.replace('__', '/')
    return await super().post(request=request, _id=_id)


@list_controller.resource()
class AppFieldListView(ListView):
  model_class = AppField
  # create_url = 'entity-list'
  delete_url = lambda self, object: f''

  @list_controller.route.get('/app_fields', response_class=HTMLResponse, name='app_fields-list')
  async def get(self, request: Request, search: Optional[str] = '', user=Depends(manager)):
    return await super().get(request=request, search=search)

  def get_table_definition(self, context):
    context['table_header'] = [
      {
        'name': 'Name', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'Label', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'Data Type', 
        'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      },
      {
        'name': 'Element Type', 
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
        'name': 'label',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'name': 'data_type',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'name': 'element_type',
        'class': 'px-6 py-4 whitespace-nowrap',
      },
      {
        'html': '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {% if object.is_active %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">{% if object.is_active %}Active{% else %}Inactive{% endif %}</span>',
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






'''
AppRelated model:
  parent_collection: str
  parent_key: str
  parent_id: str
  target_collection: str
  target_projection: List[str]
  target_url: str
  redirect_url: str
Example usage:
{
  'parent_collection': 'apps',
  'parent_key': 'app_id',
  'parent_id': '61f084bbbdf965735b554246',
  'target_collection': 'app_fields', 
  'target_projection': [
    'name', 
    'label', 
    'data_type', 
    'element_type', 
    'is_active'
  ],
  'target_url': '/app_fields',
  'redirect_url': '__apps__61f084bbbdf965735b554246',
}
'''

related_controller = get_controller()


@related_controller.resource()
class AppRelatedListView():
  request = None
  related = None

  '''
  CHANGE THE ROUTE TO INCLUDE THE ID OF THE SELECTED TAB. 
  YOU CAN THEN LOAD THE UNDERLYING CONTENT AND THEN RENDER IT...
  '''

  @related_controller.route.get('/app_related/{app_related_id}', response_class=HTMLResponse, name='app_related-list')
  async def get(self, request: Request, app_related_id: str, user=Depends(manager)):
    # payload = {
    #   'parent_collection': 'apps',
    #   'parent_key': 'app_id',
    #   'parent_id': '61f084bbbdf965735b554246',
    #   'target_collection': 'app_fields', 
    #   'target_projection': [
    #     'name', 
    #     'label', 
    #     'data_type', 
    #     'element_type', 
    #     'is_active'
    #   ],
    #   'target_url': '/app_fields',
    #   'redirect_url': '__apps__61f084bbbdf965735b554246',
    # }
    # app_related = AppRelated(**payload)
    app_related = await self.get_app_related_by_id(app_related_id)

    is_modal = False
    if app_related.target_collection != app_related.parent_collection:
      is_modal = True
    self.request = request
    self.app_related = app_related

    context = {}
    query = self.get_query()
    data = await find(query)

    context['request'] = request
    context['app_related'] = self.app_related
    context['is_modal'] = is_modal
    context['object_list'] = data

    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  async def get_app_related_by_id(self, app_related_id):
    query = Query(
      database=DATABASE_NAME,
      collection='app_related',
      query_type='find_one',
      query={'_id': app_related_id},
    )
    data = await find_one(query)
    app_related = AppRelated(**data)
    return app_related

  def get_query(self):
    projection = {}
    for p in self.app_related.target_projection:
      projection[p] = 1

    query = Query(
      database=DATABASE_NAME,
      collection=self.app_related.target_collection,
      query_type='find',
      query={f'{self.app_related.parent_key}': self.app_related.parent_id},
      projection=projection
    )
    return query

  def get_template_name(self):
    return 'crud/related_list/partials/related_list.html'

