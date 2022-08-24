import datetime
import os
from pathlib import Path
from dateutil import parser
from urllib.parse import urlparse, quote, unquote
import json
from bson import json_util, ObjectId
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_router_controller import Controller
from starlette_wtf import StarletteForm
from starlette.datastructures import MultiDict
from wtforms import Form, FormField, FieldList
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union
from mango.auth.models import Credentials
from mango.auth.auth import can, can_can
from mango.core.models import Action, Role, Model, ModelRecordType, ModelField, PageLayout, ListLayout, Tab, App, Lookup
from mango.core.fields import LookupSelectField, PicklistSelectField, QuerySelectField, QuerySelectMultipleField, StringField2, FloatField2
from mango.core.forms import get_string_form, ActionForm, RoleForm, ModelForm, ModelRecordTypeForm, ModelFieldForm, PageLayoutForm, ListLayoutForm, TabForm, AppForm, KeyValueForm, LookupForm
from mango.db.models import DateTimeAwareEncoder, datetime_parser, json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, UpdateOne, UpdateMany, Delete, DeleteOne, DeleteMany, BulkWrite, AggregatePipeline
# from mango.db.api import find, find_one, run_pipeline, delete, delete_one, update_one, insert_one
from mango.db.rest import find, find_one, run_pipeline, delete, delete_one, update_one, insert_one
from mango.template_utils.utils import configure_templates

DATABASE_NAME = os.environ.get('DATABASE_NAME')
TEMPLATE_DIRECTORY = os.environ.get('TEMPLATE_DIRECTORY')

templates = configure_templates(directory=TEMPLATE_DIRECTORY)
action_map = {
  'get_list': 'view',
  'get_list_related': 'view',
  'get_create': 'add',
  'post_create': 'add',
  'get_update': 'edit',
  'post_update': 'edit',
  'get_delete': 'delete',
  'post_delete': 'delete',
}
white_list = ['login']

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
  lookups = {'organization': {'title': 'FA'}}

  def __init__(self):
    self.can = can
    self.can_can = can_can

  async def get(self, request: Request):
    self.request = request
    self.organization = await self.get_default_organization()    
    # context = {'request': request, 'settings': settings, 'view': self}
    context = {'request': request, 'view': self}
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  def get_template_name(self):
    pass

  def get_query(self, query_type: str, collection: str, query: dict = {}, sort: dict = {}, data: dict = None):
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
        query=query,  # {'_id': self._id}
        sort=sort  # {'name': 1}
      )
    return query

  async def get_default_organization(self):
    query = self.get_query('find_one', collection='organization', query={'is_default': True})
    data = await find_one(query)
    return data


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
  template_name = f'shell/crud/list/partials/new_table_row.html'
  response = templates.TemplateResponse(template_name, context)
  return response


class BaseDynamicView():
  '''
    It depends on a model class and its meta class to provide all the necessary 
    information required for loading data for create, update, or delete.
  '''
  is_dynamic = True
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
  page_designer = None
  filter_model_name = ''
  filter_model_id = ''
  lookups = {'organization': {'title': 'TEST'}}

  def __init__(self):
    self.can = can
    self.can_can = can_can
    
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
      self.create_url = f'/view/{self.model_name}/create'
    if not self.update_url and _id:
      self.update_url = f'/view/{self.model_name}/{_id}'
    if not self.delete_url and _id:
      self.delete_url = f'/view/{self.model_name}/{_id}/delete'
    if not self.list_url:
      self.list_url = f'/view/{self.model_name}'

  async def get(self, request: Request, get_type: str, model: str, _id: str = '', search: str = '', is_modal: bool = False, user = None):
    self.request = request
    self.model_name = model
    self.model_class = self.get_model_class(model)
    self.form_class = self.get_form_class(model)
    self._id = _id
    self.search = search
    self.is_modal = is_modal
    self.initialize_route_urls(_id)

    action_permission = action_map.get(get_type, None)
    if not can(current_user=user, role='', action=f'{model}/{action_permission}'):
      context = {'request': request, 'model': model}
      template_name = f'partials/not-authorized.html'
      response = templates.TemplateResponse(template_name, context)
      return response      

    if is_modal and request.state.redirect_url:
      redirect_url_parsed = urlparse(request.state.redirect_url)
      redirect_url_parts = redirect_url_parsed.path.split('/')
      self.filter_model_name, self.filter_model_id = redirect_url_parts[2::1]
      url_parts = request.url.path.split('/')
      self.redirect_url = request.state.redirect_url

    if search:
      context = await self.get_search_context_data(request, search)
    else:
      context = await self.get_context_data(request, get_type=get_type, _id=_id)
    
    if self.page_designer:
      import os
      from jinja2 import Environment, BaseLoader, DictLoader
      from mango.template_utils.utils import (
        is_datetime,
        is_fieldlist,
        is_list,
        is_form_field,
        is_lookup_select_field,
        is_query_select_field,
        is_key_value_form,
        contains,
        endswith,
        startswith,
        to_field_list_label,
        to_proper_case,
        to_string,
        to_date,
        db_lookup,        
      )
      path = 'templates/macros/macros.html'
      full_path = os.path.join(Path.cwd(), path)
      page_markup = self.page_designer['transform']
      with open(full_path, 'r') as f:
        macro = f.read()
      markup = f'''{macro}
        {page_markup}
      '''
      env = Environment(loader=BaseLoader())

      env.filters.update({
        'is_datetime': is_datetime,
        'is_fieldlist': is_fieldlist,
        'is_list': is_list,
        'is_form_field': is_form_field,
        'is_lookup_select_field': is_lookup_select_field,
        'is_query_select_field': is_query_select_field,
        'is_key_value_form': is_key_value_form,
        'contains': contains,
        'endswith': endswith,
        'startswith': startswith,
        'to_field_list_label': to_field_list_label,
        'to_proper_case': to_proper_case,
        'to_string': to_string,
        'to_date': to_date,
        'db_lookup': db_lookup,
      })
      env.tests['is_datetime'] = is_datetime
      env.tests['is_fieldlist'] = is_fieldlist
      env.tests['is_list'] = is_list
      env.tests['is_form_field'] = is_form_field
      env.tests['is_lookup_select_field'] = is_lookup_select_field
      env.tests['is_query_select_field'] = is_query_select_field
      env.tests['is_key_value_form'] = is_key_value_form
      env.tests['contains'] = contains
      env.tests['endswith'] = endswith
      env.tests['startswith'] = startswith
      env.tests['to_field_list_label'] = to_field_list_label
      env.tests['to_proper_case'] = to_proper_case
      env.tests['to_string'] = to_string
      env.tests['to_date'] = to_date
      env.tests['db_lookup'] = db_lookup

      tmpl = env.from_string(markup)

      self.page_designer['rendered'] = tmpl.render(**context)

    template_name = self.get_template_name(get_type)
    response = templates.TemplateResponse(template_name, context)
    return response

  async def get_list_related(self, request: Request, model: str, _id: str = '', related_model: str = '', search: str = '', is_modal: bool = False, user = None):
    self.get_type = 'get_list_related'
    self.request = request
    # self.model_name = model
    self.model_name = related_model
    self.related_model_name = related_model
    self.model_class = self.get_model_class(related_model)
    self.form_class = self.get_form_class(related_model)
    self._id = _id
    self.search = search
    self.is_modal = is_modal
    self.initialize_route_urls(_id)

    self.related_query = self.build_related_query(model=model, _id=_id, related_model=related_model)

    action_permission = action_map.get(self.get_type, None)
    if not can(current_user=user, role='', action=f'{model}/{action_permission}'):
      context = {'request': request, 'model': model}
      template_name = f'partials/not-authorized.html'
      response = templates.TemplateResponse(template_name, context)
      return response      

    if is_modal and request.state.redirect_url:
      redirect_url_parsed = urlparse(request.state.redirect_url)
      redirect_url_parts = redirect_url_parsed.path.split('/')
      self.filter_model_name, self.filter_model_id = redirect_url_parts[2::1]
      self.redirect_url = request.state.redirect_url

    if search:
      context = await self.get_search_context_data(request, search)
    else:
      context = await self.get_context_data(request, get_type=self.get_type, _id=_id)
    
    if self.page_designer:
      import os
      from jinja2 import Environment, BaseLoader, DictLoader
      from mango.template_utils.utils import (
        is_datetime,
        is_fieldlist,
        is_list,
        is_form_field,
        is_lookup_select_field,
        is_query_select_field,
        is_key_value_form,
        contains,
        endswith,
        startswith,
        to_field_list_label,
        to_proper_case,
        to_string,
        to_date,
        db_lookup,        
      )
      path = 'templates/macros/macros.html'
      full_path = os.path.join(Path.cwd(), path)
      page_markup = self.page_designer['transform']
      with open(full_path, 'r') as f:
        macro = f.read()
      markup = f'''{macro}
        {page_markup}
      '''
      env = Environment(loader=BaseLoader())

      env.filters.update({
        'is_datetime': is_datetime,
        'is_fieldlist': is_fieldlist,
        'is_list': is_list,
        'is_form_field': is_form_field,
        'is_lookup_select_field': is_lookup_select_field,
        'is_query_select_field': is_query_select_field,
        'is_key_value_form': is_key_value_form,
        'contains': contains,
        'endswith': endswith,
        'startswith': startswith,
        'to_field_list_label': to_field_list_label,
        'to_proper_case': to_proper_case,
        'to_string': to_string,
        'to_date': to_date,
        'db_lookup': db_lookup,
      })
      env.tests['is_datetime'] = is_datetime
      env.tests['is_fieldlist'] = is_fieldlist
      env.tests['is_list'] = is_list
      env.tests['is_form_field'] = is_form_field
      env.tests['is_lookup_select_field'] = is_lookup_select_field
      env.tests['is_query_select_field'] = is_query_select_field
      env.tests['is_key_value_form'] = is_key_value_form
      env.tests['contains'] = contains
      env.tests['endswith'] = endswith
      env.tests['startswith'] = startswith
      env.tests['to_field_list_label'] = to_field_list_label
      env.tests['to_proper_case'] = to_proper_case
      env.tests['to_string'] = to_string
      env.tests['to_date'] = to_date
      env.tests['db_lookup'] = db_lookup

      tmpl = env.from_string(markup)

      self.page_designer['rendered'] = tmpl.render(**context)

    template_name = self.get_template_name(self.get_type)
    response = templates.TemplateResponse(template_name, context)
    return response

  def build_related_query(self, model: str, _id: str, related_model: str):
    criteria = {f'{model}_id': _id}
    query = self.get_query('find', collection=related_model, query=criteria)
    return query

  async def get_search_context_data(self, request: Request, search: str):
    form = self.form_class(request)
    self.list_layout = await self.get_list_layout(get_type='get_list')
    if self.list_layout:
      pipeline = self.get_pipeline(field_list=self.list_layout['field_list'])
    else:
      query = self.get_query('find', collection='model_field', query={'model_name': self.model_name})
      query_result = await find(query)
      field_list = [x['name'] for x in query_result]
      pipeline = self.get_pipeline(field_list=field_list)
    batch = await run_pipeline(pipeline)
    data = batch['cursor']['firstBatch']
    self.organization = await self.get_default_organization()
    context = {'request': request, 'view': self, 'data': data, 'form': form, 'search': search}
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

    self.organization = await self.get_default_organization()
    self.page_designer = await self.get_page_designer(get_type)
    self.list_layout = await self.get_list_layout(get_type)

    if get_type in ['get_update', 'get_delete']:
      model_data = self.model_class(**data)
      data_string = str(model_data)
      # raw_data = json.dumps(model_data.dict(), cls=DateTimeAwareEncoder)
      raw_data = json.dumps(model_data.dict(), default=json_from_mongo)
      self.main_class = f'{self.model_class.__module__}.{self.model_class.__name__}'
      # self.main_data = quote(raw_data)
      self.main_form = f'{self.form_class.__module__}.{self.form_class.__name__}'

    if get_type in ['get_create', 'get_update']:
      if  hasattr(self, 'form_class'):
        if issubclass(self.form_class, StarletteForm):
          form = self.form_class(request, data=data)
        elif issubclass(self.form_class, Form):
          form = self.form_class(data=data)
        for field in form:
          if isinstance(field, LookupSelectField) or isinstance(field, PicklistSelectField) or isinstance(field, QuerySelectField) or isinstance(field, QuerySelectMultipleField):
            field.choices = field.get_choices(data=data)
          elif isinstance(field, FieldList):
            for sub_field in field:
              if isinstance(sub_field, FormField):
                for sub_form_field in sub_field:
                  if isinstance(sub_form_field, FieldList):
                    for sub_sub_form_field in sub_form_field:
                      if isinstance(sub_sub_form_field, FormField):
                        for sub_sub_sub_form_field in sub_sub_form_field:
                          if isinstance(sub_sub_sub_form_field, LookupSelectField) or isinstance(sub_sub_sub_form_field, PicklistSelectField) or isinstance(sub_sub_sub_form_field, QuerySelectField) or isinstance(sub_sub_sub_form_field, QuerySelectMultipleField):
                            sub_sub_sub_form_field.choices = sub_sub_sub_form_field.get_choices(data=data)
                      elif isinstance(sub_sub_form_field, LookupSelectField) or isinstance(sub_sub_form_field, PicklistSelectField) or isinstance(sub_sub_form_field, QuerySelectField) or isinstance(sub_sub_form_field, QuerySelectMultipleField):
                        sub_sub_form_field.choices = sub_sub_form_field.get_choices(data=data)
                  elif isinstance(sub_form_field, LookupSelectField) or isinstance(sub_form_field, PicklistSelectField) or isinstance(sub_form_field, QuerySelectField) or isinstance(sub_form_field, QuerySelectMultipleField):
                    sub_form_field.choices = sub_form_field.get_choices(data=data)
              elif isinstance(sub_field, LookupSelectField) or isinstance(sub_field, PicklistSelectField) or isinstance(sub_field, QuerySelectField) or isinstance(sub_field, QuerySelectMultipleField):
                sub_field.choices = sub_field.get_choices(data=data)

    context = {'request': request, 'view': self, 'data': data, 'data_string': data_string, 'form': form}
    return context

  async def get_default_organization(self):
    query = self.get_query('find_one', collection='organization', query={'is_default': True})
    data = await find_one(query)
    return data

  async def get_page_designer(self, get_type: str):
    data = None
    if get_type in ['get_create', 'get_update']:
      query = self.get_query('find_one', collection='page_designer', query={'model_name': self.model_name})
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
      if self.filter_model_name and self.filter_model_id and not 'related_list' in self.request.url.path:
        criteria = {f'{self.filter_model_name}_id': self.filter_model_id}
        query = self.get_query('find', collection=self.model_name, query=criteria)
      else:
        query = self.get_query('find', collection=self.model_name)
      if self.model_data:
        if self.model_data.order_by:
          sort = {}
          for item in self.model_data.order_by:
            sort[item] = 1
          query.sort = sort      
      data = await find(query)
    elif get_type in ['get_list_related']:
      query = self.related_query
      if self.model_data:
        if self.model_data.order_by:
          sort = {}
          for item in self.model_data.order_by:
            sort[item] = 1
          query.sort = sort      
      data = await find(query)
    return data

  def get_query(self, query_type: str, collection: str, query: dict = {}, sort: dict = {}, data: dict = None):
    if query_type == 'find_one':
      query_def = QueryOne(
        database=DATABASE_NAME,
        collection=collection,
        query=query  # {'_id': self._id}
      )
    elif query_type == 'find':
      query_def = Query(
        database=DATABASE_NAME,
        collection=collection,
        query=query,  # {'_id': self._id}
        sort=sort  # {'name': 1}
      )
    return query_def

  def get_pipeline(self, field_list:List[str] = []):
    search_index_name = self.model_class.Meta.search_index_name
    # search_index_name = 'customer_search_standard'
    sort = {}
    if self.model_data:
      for item in self.model_data.order_by:
        sort[item] = 1
    page_size = self.model_class.Meta.page_size
    if page_size == 0:
      page_size = 30
    keys = [x for x in field_list]
    projection = {keys[i]: 1 for i in range(0, len(keys), 1)}
    project = {
      "_id": {
        "$toString": "$_id"
      },
      "score": { 
        "$meta": "searchScore" 
      }
    }
    # project = project | projection
    project = dict(list(project.items()) + list(projection.items()))
    pipeline_list = [
      {
        "$search": {
          "index": search_index_name,
          "text": {
            "query": self.search,
            "path": field_list,
            # "path": {
            #   "wildcard": "*"
            # },
            "fuzzy": {
              "maxEdits": 1,
              "prefixLength": 1,
              "maxExpansions": 5,
            }
          }
        }
      },
      {
        "$project": project
      },
      # {
      #   "$sort": sort
      # },
      {
        "$limit": page_size
      }
    ]
    print(pipeline_list)
    pipeline = AggregatePipeline(
      database=DATABASE_NAME,
      aggregate=self.model_class.Meta.name,
      pipeline=pipeline_list,
      cursor={}
    )
    return pipeline

  async def post(self, request: Request, post_type: str, model: str, _id: str = '', is_modal: bool = False, user = None):
    self.request = request
    self.model_name = model
    self.model_class = self.get_model_class(model)
    self.form_class = self.get_form_class(model)
    self._id = _id
    self.is_modal = is_modal
    self.initialize_route_urls(_id)
    temp = await request.form()
    self.form = await self.form_class.from_formdata(request)

    action_permission = action_map.get(post_type, None)
    if not can(current_user=user, role='', action=f'{model}/{action_permission}'):
      context = {'request': request, 'model': model}
      template_name = f'partials/not-authorized.html'
      response = templates.TemplateResponse(template_name, context)
      return response      

    if is_modal and request.state.redirect_url:
      self.redirect_url = request.state.redirect_url

    if post_type in ['post_update', 'post_delete']:
      data = await self.get_data('get_update')
      model_data = self.model_class(**data)
      data_string = str(model_data)
      for field in self.form:
        if isinstance(field, LookupSelectField) or isinstance(field, PicklistSelectField) or isinstance(field, QuerySelectField) or isinstance(field, QuerySelectMultipleField):
          field.choices = field.get_choices(data=data)
        elif isinstance(field, FieldList):
          for sub_field in field:
            if isinstance(sub_field, FormField):
              for sub_form_field in sub_field:
                if isinstance(sub_form_field, FieldList):
                  for sub_sub_form_field in sub_form_field:
                    if isinstance(sub_sub_form_field, FormField):
                      for sub_sub_sub_form_field in sub_sub_form_field:
                        if isinstance(sub_sub_sub_form_field, LookupSelectField) or isinstance(sub_sub_sub_form_field, PicklistSelectField) or isinstance(sub_sub_sub_form_field, QuerySelectField) or isinstance(sub_sub_sub_form_field, QuerySelectMultipleField):
                          sub_sub_sub_form_field.choices = sub_sub_sub_form_field.get_choices(data=data)
                    elif isinstance(sub_sub_form_field, LookupSelectField) or isinstance(sub_sub_form_field, PicklistSelectField) or isinstance(sub_sub_form_field, QuerySelectField) or isinstance(sub_sub_form_field, QuerySelectMultipleField):
                      sub_sub_form_field.choices = sub_sub_form_field.get_choices(data=data)
                elif isinstance(sub_form_field, LookupSelectField) or isinstance(sub_form_field, PicklistSelectField) or isinstance(sub_form_field, QuerySelectField) or isinstance(sub_form_field, QuerySelectMultipleField):
                  sub_form_field.choices = sub_form_field.get_choices(data=data)
            elif isinstance(sub_field, LookupSelectField) or isinstance(sub_field, PicklistSelectField) or isinstance(sub_field, QuerySelectField) or isinstance(sub_field, QuerySelectMultipleField):
              sub_field.choices = sub_field.get_choices(data=data)

    if post_type == 'post_create':
      data = await self.get_data('get_create')
      for field in self.form:
        if isinstance(field, LookupSelectField) or isinstance(field, PicklistSelectField) or isinstance(field, QuerySelectField) or isinstance(field, QuerySelectMultipleField):
          field.choices = field.get_choices(data=data)
      if await self.form.validate_on_submit():
        payload = self.post_query(post_type)
        response = await self.post_data(post_type, payload=payload)
      else:
        # context = {'request': request, 'settings': settings, 'view': self, 'data': {}, 'form': self.form}
        context = {'request': request, 'view': self, 'data': {}, 'form': self.form}
        template_name = self.get_template_name(post_type)
        response = templates.TemplateResponse(template_name, context)
    elif post_type == 'post_update':
      if await self.form.validate_on_submit():
        payload = self.post_query(post_type, query={'_id': self._id})
        response = await self.post_data(post_type, payload=payload)
      else:
        print('Form Errors: ', self.form.errors)
        # context = {'request': request, 'settings': settings, 'view': self, 'data': {'_id': _id}, 'data_string': data_string, 'form': self.form}
        context = {'request': request, 'view': self, 'data': {'_id': _id}, 'data_string': data_string, 'form': self.form}
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
    if http_type in ['get_list', 'get_list_related']:
      template_type = 'list'
    elif http_type in ['get_create', 'post_create']:
      template_type = 'create'
    elif http_type in ['get_update', 'post_update']:
      template_type = 'update'
    elif http_type in ['get_delete', 'post_delete']:
      template_type = 'delete'

    if self.request.state.htmx:
      return f'shell/crud/{template_type}/partials/index.html'
    else:
      return f'shell/crud/{template_type}/index.html'

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

