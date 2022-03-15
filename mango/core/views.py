import datetime
from dateutil import parser
import json
from bson import json_util, ObjectId
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_router_controller import Controller
from starlette_wtf import StarletteForm
from starlette.datastructures import MultiDict
from wtforms import Form
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union
from mango.auth.models import Credentials
from mango.auth.auth import can
from mango.core.models import Action, Role, Model, ModelRecordType, ModelField, PageLayout, ListLayout, Tab, App
from mango.core.fields import QuerySelectField, QuerySelectMultipleField, StringField2
from mango.core.forms import get_string_form, ActionForm, RoleForm, ModelForm, ModelRecordTypeForm, ModelFieldForm, PageLayoutForm, ListLayoutForm, TabForm, AppForm, KeyValueForm
from mango.db.models import datetime_parser, json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, UpdateOne, UpdateMany, Delete, DeleteOne, DeleteMany, BulkWrite, AggregatePipeline
from mango.db.api import find, find_one, run_pipeline, delete, delete_one, update_one, insert_one
import settings
from settings import manager, templates, DATABASE_NAME


def get_router(prefix: str = '', tags: List[str] = ['Views']):
  return APIRouter(
   prefix = prefix,
    tags = tags
  )

def get_controller(prefix: str = '', tags: List[str] = ['Views']):
  router = get_router(prefix=prefix, tags=tags)
  controller = Controller(router)
  return controller

def get_class(class_str: str):
  from importlib import import_module
  try:
    module_path, class_name = class_str.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)
  except (ImportError, AttributeError) as e:
    raise ImportError(class_str)


class StaticView():
  def __init__(self):
    self.can = can

  async def get(self, request: Request):
    self.request = request
    context = {'request': request, 'settings': settings, 'view': self}
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  def get_template_name(self):
    pass


router = APIRouter(
  prefix = '',
  tags = ['Helper Views']
)

@router.get('/table_row/create/{form_name}/{prefix}/{pos}', response_class=HTMLResponse, name='get_table_row_create')
async def get_new_table_row(request: Request, form_name: str, prefix: str = '', pos: int = -1):
  if pos > -1:
    prefix = f'{prefix}-{str(pos)}'
  if form_name.endswith('Form'):
    instance = get_class(form_name)
    form = instance(prefix=prefix)
  else:
    form = get_string_form(prefix=prefix)
  context = {'request': request, 'form': form, 'prefix': prefix}
  template_name = f'core/list/partials/new_table_row.html'
  response = templates.TemplateResponse(template_name, context)
  return response


class BaseView():
  '''
    It depends on a model class and its meta class to provide all the necessary 
    information required for loading data for create, update, or delete.
  '''
  template_name = ''
  model_class = None
  model_name = ''
  form_class = None
  create_route_name = ''
  update_route_name = ''
  delete_route_name = ''
  list_route_name = ''
  create_url = ''
  update_url = ''
  delete_url = ''
  list_url = ''
  redirect_url = ''
  query_type = ''

  def __init__(self):
    # if not self.template_name:
    #   raise Exception('Missing attribute template_name!')
    if not self.model_class:
      raise Exception('Missing attribute model_class!')
    self.can = can
    self.model_name = self.model_class.Meta.name
    self.initialize_route_names()
    
  def initialize_route_names(self):
    if not self.create_route_name:
      self.create_route_name = f'{self.model_name}-create'
    if not self.update_route_name:
      self.update_route_name = f'{self.model_name}-update'
    if not self.delete_route_name:
      self.delete_route_name = f'{self.model_name}-delete'
    if not self.list_route_name:
      self.list_route_name = f'{self.model_name}-list'

  def initialize_route_urls(self, _id: str = ''):
    if not self.create_url:
      self.create_url = f'/{self.model_name}/create'
    if not self.update_url and _id:
      self.update_url = f'/{self.model_name}/{_id}'
    if not self.delete_url and _id:
      self.delete_url = f'/{self.model_name}/{_id}/delete'
    if not self.list_url:
      self.list_url = f'/{self.model_name}'

  async def get(self, request: Request, get_type: str, _id: str = '', search: str = '', is_modal: bool = False):
    self.request = request
    self._id = _id
    self.search = search
    self.initialize_route_urls(_id)
    if search:
      context = await self.get_search_context_data(request, search)
    else:
      context = await self.get_context_data(request, get_type=get_type, _id=_id)
    context['is_modal'] = is_modal
    if self.redirect_url:
      context['redirect_url'] = self.redirect_url
    
    template_name = self.get_template_name(get_type)
    response = templates.TemplateResponse(template_name, context)
    return response

  async def get_search_context_data(self, request: Request, search: str):
    form = self.form_class(request)
    self.list_layout = await self.get_list_layout(get_type='get_list')
    pipeline = self.get_pipeline(field_list=self.list_layout['field_list'])
    batch = await run_pipeline(pipeline)
    data = batch['cursor']['firstBatch']
    context = {'request': request, 'settings': settings, 'view': self, 'data': data, 'form': form, 'search': search}
    return context

  async def get_context_data(self, request: Request, get_type: str, _id: str = ''):
    form = None

    if hasattr(self, 'form_class'):
      if request.method == 'GET':
        if issubclass(self.form_class, StarletteForm):
          form = self.form_class(request)
          pass
        elif issubclass(self.form_class, Form):
          form = self.form_class()
      elif request.method == 'POST':
        form = await self.form_class.from_formdata(request)

    data_string = ''

    if get_type in ['get_create']:
      data = self.model_class.new_dict()
    else:
      data = await self.get_data(get_type)

    self.page_layout = await self.get_page_layout(get_type)
    self.list_layout = await self.get_list_layout(get_type)

    if get_type in ['get_update', 'get_delete']:
      model_data = self.model_class(**data)
      data_string = str(model_data)

    if _id or get_type in ['get_create']:
      if  hasattr(self, 'form_class'):
        if issubclass(self.form_class, StarletteForm):
          form = self.form_class(request, data=data)
        elif issubclass(self.form_class, Form):
          form = self.form_class(data=data)
        for field in form:
          if isinstance(field, QuerySelectField) or isinstance(field, QuerySelectMultipleField):
            field.choices = field.get_choices(data=data)

    context = {'request': request, 'settings': settings, 'view': self, 'data': data, 'data_string': data_string, 'form': form, 'page_layout': self.page_layout}
    return context

  async def get_page_layout(self, get_type: str):
    data = None
    if get_type in ['get_create', 'get_update']:
      query = self.get_query('find_one', collection='page_layout', query={'model_name': self.model_name})
      data = await find_one(query)
    return data

  async def get_list_layout(self, get_type: str):
    data = None
    if get_type in ['get_list']:
      query = self.get_query('find_one', collection='list_layout', query={'model_name': self.model_name})
      data = await find_one(query)
    return data

  async def get_data(self, get_type: str):
    data = None
    if get_type in ['get_create']:
      pass
    elif get_type in ['get_update', 'get_delete']:
      query = self.get_query('find_one', collection=self.model_name, query={'_id': self._id})
      data = await find_one(query)
    elif get_type in ['get_list']:
      query = self.get_query('find', collection=self.model_name)
      data = await find(query)
    return data

  def get_query(self, query_type: str, collection: str, query: dict = {}, data: dict = None):
    if query_type == 'find_one':
      query = QueryOne(
        database=DATABASE_NAME,
        collection=collection,
        query=query  # {'_id': self._id}
      )
    elif query_type == 'find':
      query = Query(
        database=DATABASE_NAME,
        collection=collection,
        query=query  # {'_id': self._id}
      )

    return query

  def get_pipeline(self, field_list:[str] = []):
    search_index_name = self.model_class.Meta.search_index_name
    page_size = self.model_class.Meta.page_size
    if page_size == 0:
      page_size = 100
    keys = [x for x in field_list]
    projection = {keys[i]: 1 for i in range(0, len(keys), 1)}
    project = {
      "_id": {
        "$toString": "$_id"
      }
    }
    project = project | projection
    pipeline = AggregatePipeline(
      database=DATABASE_NAME,
      aggregate=self.model_class.Meta.name,
      pipeline=[
        {
          "$search": {
            "index": search_index_name,
            "text": {
              "query": self.search,
              "path": {
                "wildcard": "*"
              },
              "fuzzy": {}
            }
          }
        },
        {
          "$project": project
        },
        {
          "$limit": page_size
        }
      ],
      cursor={}
    )
    return pipeline

  async def post(self, request: Request, post_type: str, _id: str = '', is_modal: bool = False):
    self.request = request
    self._id = _id
    self.initialize_route_urls(_id)
    temp = await request.form()
    self.form = await self.form_class.from_formdata(request)

    if post_type in ['post_update', 'post_delete']:
      data = await self.get_data('get_update')
      model_data = self.model_class(**data)
      data_string = str(model_data)
      for field in self.form:
        if isinstance(field, QuerySelectField) or isinstance(field, QuerySelectMultipleField):
          field.choices = field.get_choices(data=data)

    if post_type == 'post_create':
      data = await self.get_data('get_create')
      for field in self.form:
        if isinstance(field, QuerySelectField) or isinstance(field, QuerySelectMultipleField):
          field.choices = field.get_choices(data=data)
      if await self.form.validate_on_submit():
        payload = self.post_query(post_type)
        response = await self.post_data(post_type, payload=payload)
      else:
        context = {'request': request, 'settings': settings, 'view': self, 'data': {}, 'form': self.form}
        template_name = self.get_template_name(post_type)
        response = templates.TemplateResponse(template_name, context)
    elif post_type == 'post_update':
      if await self.form.validate_on_submit():
        payload = self.post_query(post_type, query={'_id': self._id})
        response = await self.post_data(post_type, payload=payload)
      else:
        self.page_layout = await self.get_page_layout('get_update')
        context = {'request': request, 'settings': settings, 'view': self, 'data': {'_id': _id}, 'data_string': data_string, 'form': self.form, 'page_layout': self.page_layout}
        # context = {'request': request, 'settings': settings, 'view': self, 'data': {'_id': _id}, 'data_string': data_string, 'form': self.form}
        template_name = self.get_template_name(post_type)
        response = templates.TemplateResponse(template_name, context)
    elif post_type == 'post_delete':
      payload = self.post_query(post_type, query={'_id': self._id})
      response = await self.post_data(post_type, payload=payload)
    return response

  def post_query(self, post_type: str, query: dict = {}):
    for field in self.form:
      if isinstance(field.data, datetime.date):
        min_time = datetime.datetime.min.time()
        field.data = datetime.datetime.combine(field.data, min_time)

    if post_type == 'post_create':
      payload = InsertOne(
        database=DATABASE_NAME,
        collection=self.model_name,
        data=self.form.data,
      )
    elif post_type == 'post_update':
      payload = UpdateOne(
        database=DATABASE_NAME,
        collection=self.model_name,
        query=query,
        data={'$set': self.form.data},
      )
    elif post_type == 'post_delete':
      payload = DeleteOne(
        database=DATABASE_NAME,
        collection=self.model_name,
        query=query,
      )

    return payload

  async def post_data(self, post_type: str, payload):
    if post_type == 'post_create':
      await insert_one(payload)
    elif post_type == 'post_update':
      await update_one(payload)
    elif post_type == 'post_delete':
      await delete_one(payload)

    if self.redirect_url:
      response = RedirectResponse(url=self.redirect_url, status_code=status.HTTP_302_FOUND)
    else:
      response = RedirectResponse(url=self.list_url, status_code=status.HTTP_302_FOUND)

    return response

  def get_template_name(self, http_type: str):
    template_type = ''
    if http_type in ['get_list']:
      template_type = 'list'
    elif http_type in ['get_create', 'post_create']:
      template_type = 'create'
    elif http_type in ['get_update', 'post_update']:
      template_type = 'update'
    elif http_type in ['get_delete', 'post_delete']:
      template_type = 'delete'

    if self.request.state.htmx:
      return f'core/{template_type}/partials/index.html'
    else:
      return f'core/{template_type}/index.html'

  async def get_list(self, request: Request, is_modal: bool=False):
    pass

  async def get_create(self, request: Request, is_modal: bool=False):
    pass

  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False):
    pass

  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False):
    pass

  async def post_create(self, request: Request, is_modal: bool=False):
    pass

  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False):
    pass

  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False):
    pass


action_controller = get_controller(tags=['Action Views'])
@action_controller.resource()
class ActionView(BaseView):
  model_class = Action
  form_class = ActionForm

  def __init__(self):
    super().__init__()

  @action_controller.route.get('/action', response_class=HTMLResponse, name='action-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @action_controller.route.get('/action/create', response_class=HTMLResponse, name='action-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @action_controller.route.post('/action/create', response_class=HTMLResponse, name='action-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @action_controller.route.get('/action/{_id}', response_class=HTMLResponse, name='action-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @action_controller.route.post('/action/{_id}', response_class=HTMLResponse, name='action-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @action_controller.route.get('/action/{_id}/delete', response_class=HTMLResponse, name='action-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @action_controller.route.post('/action/{_id}/delete', response_class=HTMLResponse, name='action-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


role_controller = get_controller(tags=['Role Views'])
@role_controller.resource()
class RoleView(BaseView):
  model_class = Role
  form_class = RoleForm

  def __init__(self):
    super().__init__()

  @role_controller.route.get('/role', response_class=HTMLResponse, name='role-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @role_controller.route.get('/role/create', response_class=HTMLResponse, name='role-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @role_controller.route.post('/role/create', response_class=HTMLResponse, name='role-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @role_controller.route.get('/role/{_id}', response_class=HTMLResponse, name='role-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @role_controller.route.post('/role/{_id}', response_class=HTMLResponse, name='role-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @role_controller.route.get('/role/{_id}/delete', response_class=HTMLResponse, name='role-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @role_controller.route.post('/role/{_id}/delete', response_class=HTMLResponse, name='role-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


model_controller = get_controller(tags=['Model Views'])
@model_controller.resource()
class ModelView(BaseView):
  model_class = Model
  form_class = ModelForm

  def __init__(self):
    super().__init__()

  @model_controller.route.get('/model', response_class=HTMLResponse, name='model-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @model_controller.route.get('/model/create', response_class=HTMLResponse, name='model-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @model_controller.route.post('/model/create', response_class=HTMLResponse, name='model-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @model_controller.route.get('/model/{_id}', response_class=HTMLResponse, name='model-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @model_controller.route.post('/model/{_id}', response_class=HTMLResponse, name='model-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @model_controller.route.get('/model/{_id}/delete', response_class=HTMLResponse, name='model-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @model_controller.route.post('/model/{_id}/delete', response_class=HTMLResponse, name='model-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


model_record_type_controller = get_controller(tags=['Model Record Type Views'])
@model_record_type_controller.resource()
class ModelRecordTypeView(BaseView):
  model_class = ModelRecordType
  form_class = ModelRecordTypeForm

  def __init__(self):
    super().__init__()

  @model_record_type_controller.route.get('/model_record_type', response_class=HTMLResponse, name='model_record_type-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @model_record_type_controller.route.get('/model_record_type/create', response_class=HTMLResponse, name='model_record_type-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @model_record_type_controller.route.post('/model_record_type/create', response_class=HTMLResponse, name='model_record_type-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @model_record_type_controller.route.get('/model_record_type/{_id}', response_class=HTMLResponse, name='model_record_type-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @model_record_type_controller.route.post('/model_record_type/{_id}', response_class=HTMLResponse, name='model_record_type-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @model_record_type_controller.route.get('/model_record_type/{_id}/delete', response_class=HTMLResponse, name='model_record_type-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @model_record_type_controller.route.post('/model_record_type/{_id}/delete', response_class=HTMLResponse, name='model_record_type-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


model_field_controller = get_controller(tags=['Model Field Views'])
@model_field_controller.resource()
class ModelFieldView(BaseView):
  model_class = ModelField
  form_class = ModelFieldForm

  def __init__(self):
    super().__init__()

  @model_field_controller.route.get('/model_field', response_class=HTMLResponse, name='model_field-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @model_field_controller.route.get('/model_field/create', response_class=HTMLResponse, name='model_field-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @model_field_controller.route.post('/model_field/create', response_class=HTMLResponse, name='model_field-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @model_field_controller.route.get('/model_field/{_id}', response_class=HTMLResponse, name='model_field-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @model_field_controller.route.post('/model_field/{_id}', response_class=HTMLResponse, name='model_field-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @model_field_controller.route.get('/model_field/{_id}/delete', response_class=HTMLResponse, name='model_field-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @model_field_controller.route.post('/model_field/{_id}/delete', response_class=HTMLResponse, name='model_field-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


page_layout_controller = get_controller(tags=['Page Layout Views'])
@page_layout_controller.resource()
class PageLayoutView(BaseView):
  model_class = PageLayout
  form_class = PageLayoutForm

  def __init__(self):
    super().__init__()

  @page_layout_controller.route.get('/page_layout', response_class=HTMLResponse, name='page_layout-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @page_layout_controller.route.get('/page_layout/create', response_class=HTMLResponse, name='page_layout-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @page_layout_controller.route.post('/page_layout/create', response_class=HTMLResponse, name='page_layout-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @page_layout_controller.route.get('/page_layout/{_id}', response_class=HTMLResponse, name='page_layout-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @page_layout_controller.route.post('/page_layout/{_id}', response_class=HTMLResponse, name='page_layout-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @page_layout_controller.route.get('/page_layout/{_id}/delete', response_class=HTMLResponse, name='page_layout-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @page_layout_controller.route.post('/page_layout/{_id}/delete', response_class=HTMLResponse, name='page_layout-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


list_layout_controller = get_controller(tags=['List Layout Views'])
@list_layout_controller.resource()
class ListLayoutView(BaseView):
  model_class = ListLayout
  form_class = ListLayoutForm

  def __init__(self):
    super().__init__()

  @list_layout_controller.route.get('/list_layout', response_class=HTMLResponse, name='list_layout-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @list_layout_controller.route.get('/list_layout/create', response_class=HTMLResponse, name='list_layout-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @list_layout_controller.route.post('/list_layout/create', response_class=HTMLResponse, name='list_layout-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @list_layout_controller.route.get('/list_layout/{_id}', response_class=HTMLResponse, name='list_layout-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @list_layout_controller.route.post('/list_layout/{_id}', response_class=HTMLResponse, name='list_layout-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @list_layout_controller.route.get('/list_layout/{_id}/delete', response_class=HTMLResponse, name='list_layout-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @list_layout_controller.route.post('/list_layout/{_id}/delete', response_class=HTMLResponse, name='list_layout-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


tab_controller = get_controller(tags=['Tab Views'])
@tab_controller.resource()
class TabView(BaseView):
  model_class = Tab
  form_class = TabForm

  def __init__(self):
    super().__init__()

  @tab_controller.route.get('/tab', response_class=HTMLResponse, name='tab-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @tab_controller.route.get('/tab/create', response_class=HTMLResponse, name='tab-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @tab_controller.route.post('/tab/create', response_class=HTMLResponse, name='tab-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @tab_controller.route.get('/tab/{_id}', response_class=HTMLResponse, name='tab-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @tab_controller.route.post('/tab/{_id}', response_class=HTMLResponse, name='tab-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @tab_controller.route.get('/tab/{_id}/delete', response_class=HTMLResponse, name='tab-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @tab_controller.route.post('/tab/{_id}/delete', response_class=HTMLResponse, name='tab-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)


app_controller = get_controller(tags=['App Views'])
@app_controller.resource()
class AppView(BaseView):
  model_class = App
  form_class = AppForm

  def __init__(self):
    super().__init__()

  @app_controller.route.get('/app', response_class=HTMLResponse, name='app-list')
  async def get_list(self, request: Request, search: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_list', search=search, is_modal=is_modal)

  @app_controller.route.get('/app/create', response_class=HTMLResponse, name='app-create')
  async def get_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_create', is_modal=is_modal)

  @app_controller.route.post('/app/create', response_class=HTMLResponse, name='app-create')
  async def post_create(self, request: Request, is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_create', is_modal=is_modal)

  @app_controller.route.get('/app/{_id}', response_class=HTMLResponse, name='app-update')
  async def get_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_update', _id=_id, is_modal=is_modal)

  @app_controller.route.post('/app/{_id}', response_class=HTMLResponse, name='app-update')
  async def post_update(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_update', _id=_id, is_modal=is_modal)

  @app_controller.route.get('/app/{_id}/delete', response_class=HTMLResponse, name='app-delete')
  async def get_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().get(request=request, get_type='get_delete', _id=_id, is_modal=is_modal)

  @app_controller.route.post('/app/{_id}/delete', response_class=HTMLResponse, name='app-delete')
  async def post_delete(self, request: Request, _id: str = '', is_modal: bool=False, user=Depends(manager)):
    return await super().post(request=request, post_type='post_delete', _id=_id, is_modal=is_modal)
