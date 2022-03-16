import os
import importlib
from importlib.abc import Loader as _Loader, MetaPathFinder as _MetaPathFinder
import sys
from pydantic import BaseModel
from typing import List
from mango.core.models import App, Model, ModelField
from mango.db.models import Query, QueryOne
# from mango.db.api import find_sync
from mango.db.rest import find_sync, bulk_read_sync

DATABASE_NAME = os.environ.get('DATABASE_NAME')
PATH = sys.path[0]

host = None
templates = None
registered_apps = []
model_list = []
model_field_list = []


class RegisteredApp(BaseModel):
  model: Model
  fields: List[ModelField]


def init_app_loader(config_templates = None, config_host = None):
  global host
  global templates
  host = config_host
  templates = config_templates

def get_apps():
  global registered_apps
  return registered_apps

def get_registered_apps():
  global registered_apps
  registered_apps = []
  global model_list
  global model_field_list
  model_list = []
  model_field_list = []
  model_query = Query(
    database=DATABASE_NAME,
    collection='model',
    query_type='find',
    query={'is_custom': True, 'is_active': True},
  )
  model_result = find_sync(query=model_query)
  for item in model_result:
    model_list.append(Model(**item))
  batch = []
  for model in model_list:
    model_field_query = Query(
      database=DATABASE_NAME,
      collection='model_field',
      query_type='find',
      query={'model_name': model.name, 'is_active': True},
    )
    model_field_list = []
    model_field_result = find_sync(model_field_query)
    for model_field in model_field_result:
      model_field_list.append(ModelField(**model_field))
    registered_apps.append(RegisteredApp(model=model, fields=model_field_list))

def get_batch_registered_apps():
  global registered_apps
  registered_apps = []
  global model_list
  global model_field_list
  model_list = []
  model_field_list = []
  model_query = Query(
    database=DATABASE_NAME,
    collection='model',
    query_type='find',
    query={'is_custom': True, 'is_active': True},
  )
  model_result = find_sync(query=model_query)
  for item in model_result:
    model_list.append(Model(**item))
  batch = []
  for item in model_list:
    batch.append(
      Query(
        database=DATABASE_NAME,
        collection='model_field',
        query_type='find',
        query={'model_name': item.name, 'is_active': True},
      )
    )    
  [model_field_result] = bulk_read_sync(batch)
  for item in model_field_result:
    model_field_list.append(ModelField(**item))

  print('finished loading apps...')

def get_registered_app(name):
  global registered_apps
  return next((x for x in registered_apps if x.model.name == name), None)

def load_templates():
  forms_j2 = templates.get_template('apps/forms.j2')
  models_j2 = templates.get_template('apps/models.j2')
  views_j2 = templates.get_template('apps/views.j2')
  registration_j2 = templates.get_template('apps/registration.j2')
  return forms_j2, models_j2, views_j2, registration_j2

def compile_code(module, code, global_dict = {}):
  exec(code, global_dict)
  module.code = code
  return module

def import_apps():
  get_registered_apps()
  apps = get_apps()
  for item in apps:
    importlib.import_module(f'{item.model.name}__c')
    # script = f'import {name}'
    # exec(script, globals(), locals())


class CodeLoader(_Loader):

  def create_module(self, spec):
      return None

  def exec_module(self, module):
    # force reload of registered apps
    get_registered_apps()
    # get templates
    forms_j2, models_j2, views_j2, registration_j2 = load_templates()
    # get registered app
    name = module.__name__.replace('__c', '')
    ra = get_registered_app(name)
    if ra is None:
      return
    forms_tmpl = forms_j2.render(ra = ra)
    # f = open(f'/Users/summit/Documents/{name}_form.py', 'w')
    # f.write(forms_tmpl)
    # f.close()
    models_tmpl = models_j2.render(ra = ra)
    # f = open(f'/Users/summit/Documents/{name}_model.py', 'w')
    # f.write(models_tmpl)
    # f.close()
    views_tmpl = views_j2.render(ra = ra)
    # f = open(f'/Users/summit/Documents/{name}_view.py', 'w')
    # f.write(views_tmpl)
    # f.close()
    registration_tmpl = registration_j2.render(ra = ra)
    code = f"""{models_tmpl}{forms_tmpl}{views_tmpl}{registration_tmpl}"""
    # f = open(f'/Users/summit/Documents/{name}_full.py', 'w')
    # f.write(code)
    # f.close()
    context = {'app': host}
    compile_code(module, code, context)


class CodeFinder(_MetaPathFinder):

    def find_module(self, fullname, path=PATH):
        return self.find_spec(fullname, path)

    def find_spec(self, fullname, path, target = None):
        from importlib.machinery import ModuleSpec
        fullname = fullname.split(sep='.')[-1]
        if '.' in fullname:
            raise NotImplementedError()

        if fullname.endswith('__c'):
          return ModuleSpec(fullname, CodeLoader())
        else:
            return None


sys.meta_path.append(CodeFinder())