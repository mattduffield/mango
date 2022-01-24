import os
from importlib.abc import Loader as _Loader, MetaPathFinder as _MetaPathFinder
import sys
from mango.core.models import App
from mango.db.models import Query
from mango.db.api import find_sync

DATABASE_NAME = os.environ.get('DATABASE_NAME')
PATH = sys.path[0]

host = None
templates = None
registered_apps = []

def init_config(config_templates = None, config_host = None):
  global host
  global templates
  host = config_host
  templates = config_templates

def get_registered_apps():
  global registered_apps
  registered_apps = []
  query = Query(
    database=DATABASE_NAME,
    collection='apps',
    query_type='find',
    query={'is_active': True},
  )
  result = find_sync(query)
  for item in result:
    registered_apps.append(App(**item))

def get_registered_app(name):
  global registered_apps
  return next((x for x in registered_apps if x.name == name), None)

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
    models_tmpl = models_j2.render(ra = ra)
    views_tmpl = views_j2.render(ra = ra)
    registration_tmpl = registration_j2.render(ra = ra)
    code = f"""{models_tmpl}{forms_tmpl}{views_tmpl}{registration_tmpl}"""

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