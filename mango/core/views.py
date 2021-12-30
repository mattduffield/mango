import json
from bson import json_util, ObjectId
from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)
from mango.auth.models import Credentials
from mango.db.query import datetime_parser, json_from_mongo, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
from mango.db.api import find, find_one, run_pipeline, delete, update_one, insert_one
from settings import templates, DATABASE_NAME

from fastapi_router_controller import Controller



def get_router(prefix: str = '', tags: List[str] = ['Views']):
  return APIRouter(
   prefix = prefix,
    tags = tags
  )

def get_controller(prefix: str = '', tags: List[str] = ['Views']):
  router = get_router(prefix=prefix, tags=tags)
  controller = Controller(router)
  return controller


class StaticView():
  async def get(self, request: Request):
    self.request = request
    context = {'request': request}
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  def get_template_name(self):
    pass


class BaseView():
  '''
    It depends on a model class and its meta class to provide all the necessary 
    information required for loading data for create, update, or delete.
  '''
  template_name = ''
  model_name = ''
  model_name_plural = ''
  object_display = lambda self, object: f''
  list_url = ''
  create_url = ''
  delete_url = lambda self, object: f''
  query_type = ''

  def __init__(self):
    if not self.template_name:
      raise Exception('Missing attribute template_name!')
    if bool(hasattr(self, 'model_name') and self.model_name and hasattr(self, 'model_name_plural') and self.model_name_plural):
      pass
    else:
      if not hasattr(self, 'model_class'):
        raise Exception('Missing attribute model_class!')
      if not hasattr(self.model_class, 'Meta'):
        raise Exception(f'Missing attribute Meta on {self.model_class} class!')
      if not hasattr(self.model_class.Meta, 'model_name'):
        raise Exception(f'Missing attribute model_name on Meta on {self.model_class} class!')
      if not hasattr(self.model_class.Meta, 'model_name_plural'):
        raise Exception(f'Missing attribute model_name_plural on Meta on {self.model_class} class!')
      self.model_name = self.model_class.Meta.model_name
      self.model_name_plural = self.model_class.Meta.model_name_plural
    self.list_url = f'{self.model_name}-list'
    self.create_url = f'{self.model_name}-create'

  async def get(self, request: Request, _id: str = ''):
    self.request = request
    self._id = _id
    context = await self.get_context_data(request, _id)
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  async def post(self, request: Request, _id: str = ''):
    pass

  def get_template_name(self):
    pass

  # def set_form(self, form, data):
  #   if data and form:
  #     for prop in data:
  #       if hasattr(form, prop):
  #         if form[prop].type == 'FormField':
  #           for sub_prop in data[prop]:
  #             form[prop].form[sub_prop].data = data[prop][sub_prop]
  #         else:
  #           form[prop].data = data[prop]
  #   return form

  async def get_context_data(self, request, _id: str = ''):
    context = {'request': request, 'MODEL_NAME_PLURAL': self.model_name_plural, 'MODEL_NAME': self.model_name, 'OBJECT_DISPLAY': self.object_display, 'list_url': self.list_url, 'create_url': self.create_url, 'delete_url': self.delete_url}
    form = None
    form = self.form_class(request)
    if hasattr(self, 'form_class') and self.form_class:
      form = await self.form_class.from_formdata(request)
      context['form'] = form
    if _id:
      data = await self.get_queryset()
      if data and form:
        for prop in data:
          if hasattr(form, prop):
            if form[prop].type == 'FormField':
              for sub_prop in data[prop]:
                form[prop].form[sub_prop].data = data[prop][sub_prop]
            else:
              form[prop].data = data[prop]
      context['object'] = data
      context['_id'] = _id
    else:
      context['object'] = {}
    return context

  async def get_queryset(self):
    query = self.get_query()
    data = await find_one(query)
    return data

  def get_query(self):
    query = Query(
      database=DATABASE_NAME,
      collection=self.model_name_plural,
      query_type=self.query_type,
      query={'_id': self._id}
    )
    return query

  async def get_lookups(self, collection, query_type = 'find', query = {}, projection = {'name': 1, 'value': 1, '_id': 0}):
    query = Query(
      database=DATABASE_NAME,
      collection=collection,
      query_type=query_type,
      query=query,
      projection=projection
    )
    lookups = await find(query)
    return lookups


class View():
  template_name = ''
  model_name = ''
  model_name_plural = ''
  object_display = lambda self, object: f''
  list_url = ''
  create_url = ''
  delete_url = lambda self, object: f''
  query_type = ''

  def __init__(self):
    self.list_url = f'{self.model_name}-list'
    self.create_url = f'{self.model_name}-create'

  async def get(self, request: Request, _id: str = ''):
    context = await self.get_context_data(request, _id)
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  def get_template_name(self):
    pass

  async def get_context_data(self, request, _id: str = ''):
    context = {'request': request, 'MODEL_NAME_PLURAL': self.model_name_plural, 'MODEL_NAME': self.model_name, 'OBJECT_DISPLAY': self.object_display, 'list_url': self.list_url, 'create_url': self.create_url, 'delete_url': self.delete_url}
    if self.form_class:
      form = await self.form_class.from_formdata(request)
      context['form'] = form
    if _id:
      query = self.get_query(_id)
      data = await find_one(query)
      if data and form:
        for prop in data:
          if hasattr(form, prop):
            form[prop].data = data[prop]
      context['object'] = data
      context['_id'] = _id
    return context

  def get_query(self, _id: str):
    query = Query(
      database=DATABASE_NAME,
      collection=self.model_name_plural,
      query_type=self.query_type,
      query={'_id': _id}
    )
    return query

  async def get_lookups(self, collection, query_type = 'find', query = {}, projection = {'name': 1, 'value': 1, '_id': 0}):
    query = Query(
      database=DATABASE_NAME,
      collection=collection,
      query_type=query_type,
      query=query,
      projection=projection
    )
    lookups = await find(query)
    return lookups


class CreateView(BaseView):
  template_name = 'crud/item/create.html'
  query_type = 'find'
  insert_type = 'insert_one'

  def __init__(self):
    super().__init__()

  def get_template_name(self):
    if self.request.state.htmx:
      return 'crud/item/partials/create.html'
    else:
      return 'crud/item/create.html'

  async def get(self, request: Request):
    return await super().get(request=request)

  async def post(self, request: Request):
    self.request = request
    form = await self.form_class.from_formdata(request)

    if await form.validate_on_submit():
      payload = InsertOne(
        database=DATABASE_NAME,
        collection=self.model_name_plural,
        insert_type=self.insert_type,
        data=form.data,
      )
      await insert_one(payload)
      response = RedirectResponse(url=request.url_for(self.list_url), status_code=status.HTTP_302_FOUND)
    else:
      context = {'request': request, 'MODEL_NAME_PLURAL': self.model_name_plural, 'MODEL_NAME': self.model_name, 'OBJECT_DISPLAY': self.object_display, 'list_url': self.list_url, 'create_url': self.create_url, 'delete_url': self.delete_url}
      context['form'] = form
      context['object'] = {}
      template_name = self.get_template_name()
      response = templates.TemplateResponse(template_name, context)

    return response


class UpdateView(BaseView):
  template_name = 'crud/item/update.html'
  query_type = 'find_one'
  update_type = 'update_one'

  def __init__(self):
    super().__init__()

  def get_template_name(self):
    if self.request.state.htmx:
      return 'crud/item/partials/update.html'
    else:
      return 'crud/item/update.html'

  async def get(self, request: Request, _id: str):
    return await super().get(request=request, _id=_id)

  async def post(self, request: Request, _id: str):
    self.request = request
    self._id = _id
    form = await self.form_class.from_formdata(request)

    if not self._id:
      raise Exception('Missing attribute!')

    if await form.validate_on_submit():
      payload = Update(
        database=DATABASE_NAME,
        collection=self.model_name_plural,
        update_type=self.update_type,
        query={'_id': self._id},
        data={'$set': form.data},
      )
      await update_one(payload)
      response = RedirectResponse(url=request.url_for(self.list_url), status_code=status.HTTP_302_FOUND)
    else:
      context = {'request': request, 'MODEL_NAME_PLURAL': self.model_name_plural, 'MODEL_NAME': self.model_name, 'OBJECT_DISPLAY': self.object_display, 'list_url': self.list_url, 'create_url': self.create_url, 'delete_url': self.delete_url}
      context['form'] = form
      context['object'] = {'_id': _id, 'name': form.name.data}
      template_name = self.get_template_name()
      response = templates.TemplateResponse(template_name, context)

    return response


class DeleteView(BaseView):
  template_name = 'crud/item/delete.html'
  delete_url = lambda self, model_name_plural, _id: f'/{model_name_plural}/{_id}/delete'
  delete_type = 'delete_one'

  def __init__(self):
    super().__init__()

  def get_template_name(self):
    if self.request.state.htmx:
      return 'crud/item/partials/delete.html'
    else:
      return 'crud/item/delete.html'

  async def get(self, request: Request, _id: str):
    return await super().get(request=request, _id=_id)

  async def post(self, request: Request, _id: str = ''):
    self.request = request
    self._id = _id

    if not self._id:
      raise Exception('Missing attribute!')

    payload = Delete(
      database=DATABASE_NAME,
      collection=self.model_name_plural,
      delete_type=self.delete_type,
      query={'_id': self._id},
    )
    await delete(payload)
    response = RedirectResponse(url=request.url_for(self.list_url), status_code=status.HTTP_302_FOUND)
    return response


class ListView():
  '''
    This class is optimized to work with Atlas Search. It depends on a model class and 
    its meta class to provide all the necessary information required for loading data.
  '''
  template_name = 'crud/list/list.html'
  model_name = ''
  model_name_plural = ''
  object_display = lambda self, object: f''
  list_url = ''
  create_url = ''
  delete_url = lambda self, object: f''
  query_type = 'find'

  def __init__(self):
    if bool(hasattr(self, 'model_name') and self.model_name and hasattr(self, 'model_name_plural') and self.model_name_plural):
      pass
    else:
      if not hasattr(self, 'model_class'):
        raise Exception('Missing attribute model_class!')
      if not hasattr(self.model_class, 'Meta'):
        raise Exception(f'Missing attribute Meta on {self.model_class} class!')
      if not hasattr(self.model_class.Meta, 'model_name'):
        raise Exception(f'Missing attribute model_name on Meta on {self.model_class} class!')
      if not hasattr(self.model_class.Meta, 'model_name_plural'):
        raise Exception(f'Missing attribute model_name_plural on Meta on {self.model_class} class!')
      if not hasattr(self.model_class.Meta, 'search_by'):
        raise Exception(f'Missing attribute search_by on Meta on {self.model_class} class!')
      if not hasattr(self.model_class.Meta, 'search_index_name'):
        raise Exception(f'Missing attribute search_index_name on Meta on {self.model_class} class!')
      self.model_name = self.model_class.Meta.model_name
      self.model_name_plural = self.model_class.Meta.model_name_plural
      self.search_by = self.model_class.Meta.search_by
    self.list_url = f'{self.model_name}-list'
    self.create_url = f'{self.model_name}-create'

  async def get(self, request: Request, search: Optional[str] = ''):
    self.request = request
    self.search = search
    context = await self.get_context_data(request, search)
    self.get_table_definition(context)
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  def get_template_name(self):
    if self.request.state.htmx:
      return 'crud/list/partials/list.html'
    else:
      return 'crud/list/list.html'

  def get_table_definition(self, context):
    pass

  async def get_context_data(self, request, search: Optional[str] = ''):
    context = {'request': request, 'MODEL_NAME_PLURAL': self.model_name_plural, 'MODEL_NAME': self.model_name, 'OBJECT_DISPLAY': self.object_display, 'list_url': self.list_url, 'create_url': self.create_url, 'delete_url': self.delete_url}
    context['search'] = search
    context['object_list'] = await self.get_queryset()
    return context

  async def get_queryset(self):
    query = self.get_query()
    page_size = self.model_class.Meta.page_size
    # keys = [x for x in self.model_class.schema().get('properties').keys()]
    # projection = {keys[i]: 1 for i in range(0, len(keys), 1)}
    # query.projection = projection

    if self.search:
      pipeline = self.get_pipeline()
      batch = await run_pipeline(pipeline)
      data = batch['cursor']['firstBatch']
    else:
      query = self.get_query()
      query.limit = page_size
      data = await find(query)

    return data

  def get_query(self):
    query = Query(
      database=DATABASE_NAME,
      collection=self.model_name_plural,
      query_type=self.query_type
    )
    return query

  def get_pipeline(self):
    search_index_name = self.model_class.Meta.search_index_name
    page_size = self.model_class.Meta.page_size
    keys = [x for x in self.model_class.Meta.list_fields]
    projection = {keys[i]: 1 for i in range(0, len(keys), 1)}
    project = {
      "_id": {
        "$toString": "$_id"
      }
    }
    project = project | projection
    pipeline = AggregatePipeline(
      database=DATABASE_NAME,
      aggregate=self.model_name_plural,
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


class GenericListView():
  template_name = 'crud/list/list.html'
  model_name = ''
  model_name_plural = ''
  object_display = lambda self, object: f''
  list_url = ''
  create_url = ''
  delete_url = lambda self, object: f''
  query_type = 'find'
  search_by = ''
  page_size = 15
  list_fields = []

  def __init__(self):
    if not self.model_name:
      raise Exception(f'Missing attribute model_name!')
    if not self.model_name_plural:
      raise Exception(f'Missing attribute model_name_plural!')
    if not self.search_by:
      raise Exception(f'Missing attribute search_by!')
    if len(self.list_fields) == 0:
      raise Exception(f'Please provide at least one list_field entry!')
    self.list_url = f'{self.model_name}-list'
    self.create_url = f'{self.model_name}-create'

  async def get(self, request: Request, search: Optional[str] = ''):
    self.request = request
    self.search = search
    context = await self.get_context_data(request, search)
    self.get_table_definition(context)
    template_name = self.get_template_name()
    response = templates.TemplateResponse(template_name, context)
    return response

  def get_template_name(self):
    if self.request.state.htmx:
      return 'crud/list/partials/list.html'
    else:
      return 'crud/list/list.html'

  def get_table_definition(self, context):
    pass

  async def get_context_data(self, request, search: Optional[str] = ''):
    context = {'request': request, 'MODEL_NAME_PLURAL': self.model_name_plural, 'MODEL_NAME': self.model_name, 'OBJECT_DISPLAY': self.object_display, 'list_url': self.list_url, 'create_url': self.create_url, 'delete_url': self.delete_url}
    context['search'] = search
    context['object_list'] = await self.get_queryset()
    return context

  async def get_queryset(self):
    query = self.get_query()

    pipeline = self.get_pipeline()
    batch = await run_pipeline(pipeline)
    data = batch['cursor']['firstBatch']

    return data

  def get_query(self):
    query = Query(
      database=DATABASE_NAME,
      collection=self.model_name_plural,
      query_type=self.query_type
    )
    return query

  def get_pipeline(self):
    page_size = self.page_size
    keys = [x for x in self.list_fields]
    projection = {keys[i]: 1 for i in range(0, len(keys), 1)}
    project = {
      "_id": {
        "$toString": "$_id"
      }
    }
    project = project | projection
    pipeline = AggregatePipeline(
      database=DATABASE_NAME,
      aggregate=self.model_name_plural,
      # This pipeline is less efficient when dealing with large datasets.
      # Use Atlas Search instead for more efficient searches.
      pipeline=[
        {
          "$match": {
            self.search_by: {"$regex" : self.search , "$options" : "i"}
          },
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