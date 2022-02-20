'''
  Reference:
    https://github.com/dldevinc/jinja2-simple-tags
    https://michaelabrahamsen.com/posts/jinja2-custom-template-tags/
'''
from dotenv import load_dotenv
load_dotenv()
import os
import datetime
from fastapi.templating import Jinja2Templates
from jinja2_simple_tags import StandaloneTag
from wtforms import fields
from mango.db.api import find_sync, find_one_sync
from mango.db.models import Query, QueryOne
from core.fields import QuerySelectField, QuerySelectMultipleField

DATABASE_NAME = os.environ.get('DATABASE_NAME')

templates = None

'''
  The following can be used as either a filter or a test.

  Usage:
  As filter:
    field.get('field') | is_fieldlist
  As test:
    field.get('field') is is_fieldlist
  Reference:
  https://stackoverflow.com/questions/11947325/how-to-test-for-a-list-in-jinja2
  https://www.webforefront.com/django/usebuiltinjinjafilters.html
  https://gist.github.com/jb-l/466eb6a96e39bf2d92500fe8d6909b14
  https://stackoverflow.com/questions/54715768/how-to-enter-a-list-in-wtforms
'''

def is_datetime(value, *args, **kwargs):
  return isinstance(value, datetime.datetime)

def is_fieldlist(value, *args, **kwargs):
  return isinstance(value, fields.FieldList)

def is_list(value, *args, **kwargs):
  return isinstance(value, list)

def is_query_select_field(value, *args, **kwargs):
  return isinstance(value, QuerySelectField)

def to_proper_case(value, *args, **kwargs):
  if not value:
    return value
  return value.replace('_', ' ').title()

def to_string(value, *args, **kwargs):
  if not value:
    return value
  return str(value)

def to_date(value, *args, **kwargs):
  if isinstance(value, (datetime.datetime)):
    return value.strftime('%m/%d/%Y')

def db_lookup(value, data = []):
  if isinstance(value, (QuerySelectField)):
    query = Query(
      database=DATABASE_NAME,
      collection=value.collection,
      query=value.query,
      projection=value.projection
    )
    display_member = value.display_member
    value_member = value.value_member
    lookup = find_sync(query)
    found = next((display_member(x) for x in lookup if value_member(x) == data), None)
    return found
  elif isinstance(value, (QuerySelectMultipleField)):
    query = Query(
      database=DATABASE_NAME,
      collection=value.collection,
      query=value.query,
      projection=value.projection
    )
    display_member = value.display_member
    value_member = value.value_member
    lookup = find_sync(query)
    processed = []
    for item in data:
      p = next((display_member(x) for x in lookup if value_member(x) == item), None)
      processed.append(p)
    return processed
  else:
    return value


class CustomJinja2Templates(Jinja2Templates):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.env.add_extension(RenderColTag)
    self.env.filters.update({
      'is_datetime': is_datetime,
      'is_fieldlist': is_fieldlist,
      'is_list': is_list,
      'is_query_select_field': is_query_select_field,
      'to_proper_case': to_proper_case,
      'to_string': to_string,
      'to_date': to_date,
      'db_lookup': db_lookup,
    })
    self.env.tests['is_datetime'] = is_datetime
    self.env.tests['is_fieldlist'] = is_fieldlist
    self.env.tests['is_list'] = is_list
    self.env.tests['is_query_select_field'] = is_query_select_field
    self.env.tests['to_proper_case'] = to_proper_case
    self.env.tests['to_string'] = to_string
    self.env.tests['to_date'] = to_date
    self.env.tests['db_lookup'] = db_lookup


class RenderColTag(StandaloneTag):
  tags = {'RenderCol'}

  def render(self, col, instance):
    # Usage:
    #   {% RenderCol col=col, instance=object %}
    result = ''
    name = col.get('name')
    html = col.get('html')
    actions = col.get('actions')
    if name and instance:
      result = instance.get(name, '')
      format = col.get('format')
      if format:
        fmt = getattr(result, format)
        if fmt:
          result = fmt()
      if callable(result):
        result = result()
    if html and instance:
      context = {'object': instance}
      template = self.environment.from_string(html)
      result = template.render(context)
    if actions and instance:
      partials = []
      context = {'object': instance}
      result = ' '.join([self.environment.from_string(item).render(context) for item in actions])
      # for action in actions:
      #   template = self.environment.from_string(action)
      #   partials.append(template.render(context))
      # result = ' '.join(partials)
    return result


def register_tags(templates):
  templates.env.add_extension(RenderColTag)

def configure_templates(directory='templates'):
  global templates
  templates = CustomJinja2Templates(directory="templates")
  register_tags(templates)
  return templates

