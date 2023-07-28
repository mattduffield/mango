'''
  Reference:
    https://github.com/dldevinc/jinja2-simple-tags
    https://michaelabrahamsen.com/posts/jinja2-custom-template-tags/
'''
import html
import os
import datetime
import json
import pytz
from urllib.parse import quote, unquote
from fastapi.templating import Jinja2Templates
from jinja2_simple_tags import StandaloneTag
from wtforms import fields, FormField
from mango.db.rest import find_sync, find_one_sync
from mango.db.models import Query, QueryOne
from mango.core.fields import LookupSelectField, QuerySelectField, QuerySelectMultipleField, HiddenField2
from mango.core.fields import (
  ColorField2 as ColorField,
  CurrencyField2 as CurrencyField,
  DateField2 as DateField,
  DateTimeField2 as DateTimeField,
  DecimalField2 as DecimalField,
  EmailField2 as EmailField,
  FloatField2 as FloatField,
  HiddenField2 as HiddenField,
  IntegerField2 as IntegerField,
  StringField2 as StringField,
  TextAreaField2 as TextAreaField,
  FieldList2 as FieldList
)
from mango.core.forms import KeyValueForm

DATABASE_NAME = os.environ.get('DATABASE_NAME')

templates = None
lookup_cache = {}

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

def get_value(data, field_name):
  try:
    # Split the field_name into individual parts
    parts = field_name.split('.')
    # Traverse the nested structure of data
    for part in parts:
      if part.endswith(']'):
        # Handle list indexing
        index = int(part.split('[')[1][:-1])
        data = data[index]
      elif part.isdigit():
        index = int(part)
        data = data[index]
      else:
        data = data[part]
    return data
  except (KeyError, IndexError, TypeError):
    return None
    
def dot(value, expr:str = '', *args, **kwargs):
  expr_parts = expr.split('.')
  result = value
  for part in expr_parts:
    if part.isdigit():
      result = result[int(part)]
    else:
      result = result.get(part, '')
  return result

def walk_dot(value, expr:str = '', *args, **kwargs):
  expr_parts = expr.replace('-', '.').split('.')
  result = value
  for part in expr_parts:
    result = result.get(part, '')
  return result

def walk_dot_form(value, expr:str = '', *args, **kwargs):
  expr_parts = expr.split('.')
  result = value
  for part in expr_parts:
    if isinstance(result, fields.FormField):
      result = result.form[part]
    else:
      result = result[part]
  return result

def escape(value):
  '''
  Escapes special characters for rendering as HTML.
  '''
  return html.escape(str(value))

# {% set found_field = fields|find_in('name', 'product_id') %}
def find_in(value, property_name:str = None, property_value:str = None):
  if not property_name:
    raise Exception('property_name is required!')
  if not property_value:
    raise Exception('property_value is required!')
  found = next((x for x in value if x[property_name] == property_value), None)
  return found

def from_json(value, escape_newline:bool = False, *args, **kwargs):
  if escape_newline:
    value = unquote(value)
    value = value.replace('\n', '\\n')
  return json.loads(value)

def has_attr(value, attribute_name:str = '', *args, **kwargs):
  return hasattr(value, attribute_name)

def is_datetime(value, *args, **kwargs):
  return isinstance(value, datetime.datetime)

def is_fieldlist(value, *args, **kwargs):
  return isinstance(value, fields.FieldList)

def is_hiddenfield(value, *args, **kwargs):
  return isinstance(value, HiddenField2)

def is_list(value, *args, **kwargs):
  return isinstance(value, list)

def is_currency_field(value, *args, **kwargs):
  return isinstance(value, CurrencyField)

def is_form_field(value, *args, **kwargs):
  return isinstance(value, FormField)

def is_query_select_field(value, *args, **kwargs):
  return isinstance(value, QuerySelectField)

def is_lookup_select_field(value, *args, **kwargs):
  return isinstance(value, LookupSelectField)

def is_key_value_form(value, *args, **kwargs):
  return isinstance(value, KeyValueForm)

def contains(value:str, pattern:str, *args, **kwargs):
  return pattern in value

def endswith(value:str, pattern:str, *args, **kwargs):
  return value.endswith(pattern)

def startswith(value:str, pattern:str, *args, **kwargs):
  return value.startswith(pattern)

def to_phone_number(value, *args, **kwargs):
  if not value:
    return value
  clean = value.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
  if len(clean) != 10:
    return value
  area = clean[:3]
  first = clean[3:6]
  second = clean[6:10]
  return f'({area}) {first}-{second}'

def to_params(value, *args, **kwargs):
  if not value:
    return value
  result = []
  parts = value.split(',')
  for part in parts:
    result.append(f'''{part}: getValueById('{part}')''')
  if len(result) > 0:
    return ', '.join(result)
  return ''

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
  else:
    try:
      dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
      return dt.strftime('%m/%d/%Y')
    except:
      pass

def to_date_time(value, *args, **kwargs):
  if isinstance(value, (datetime.datetime)):
    return value.strftime('%m/%d/%Y %H:%M%:%S')
  else:
    try:
      dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
      return dt.strftime('%m/%d/%Y %H:%M%:%S')
    except:
      pass

def to_date_format(value, format='%m/%d/%Y', timezone='America/New_York', *args, **kwargs):
  if isinstance(value, (datetime.datetime)):
    return value.strftime(format)
  else:
    try:
      dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
      local_tz = pytz.timezone(timezone)
      local_date = dt.astimezone(local_tz)
      local_date_string = local_date.strftime(format)
      return local_date_string
    except:
      pass

def to_field_list_label(value, *args, **kwargs):
  if not value:
    return value
  _, part = value.rsplit('-', 1)
  return part.replace('_', ' ')

def to_number_format(value, *args, **kwargs):
  return format(int(value), ',')

def to_float_format(value, expr=',.2f', *args, **kwargs):
  if isinstance(value, object):
    value = str(value)
  if not value:
    return value
  result = format(float(value), expr)
  return result


def to_currency(value, *args, **kwargs):
  value = float(value)
  return "${:,.2f}".format(value)

def to_current_date(value, *args, **kwargs):
  return datetime.datetime.now().date()

def load_sync(query):
  if query.collection == 'lookup':
    lookup_name = query.query['name']
    query_encoded = quote(str(query.query))
    key = f'{query.collection}_{query_encoded}_{lookup_name}'
    if not key in lookup_cache:
      lookup = find_one_sync(query)
      lookup = lookup['item_list']
      lookup_cache[key] = lookup
    else:
      lookup = lookup_cache[key]
  #
  # TODO: NEED TO HAVE A BETTER APPROACH TO CACHING...
  #       CURRENTLY, WE NEED THIS FOR LIST VIEWS AND ANY LOOKUPS
  #       USED PER ROW...
  #
  # else:
  #   lookup = find_sync(query)
  #   lookup_cache[query.collection] = lookup
  elif not query.collection in lookup_cache:
    lookup = find_sync(query)
    lookup_cache[query.collection] = lookup
  else:
    lookup = lookup_cache[query.collection]
  return lookup

def db_lookup(value, data = [], lookups = {}):
  if isinstance(value, (LookupSelectField)):
    if any(value.query):
      for prop in value.query:
        if callable(value.query[prop]):
          value.query[prop] = value.query[prop](data)
      query = QueryOne(
        database=DATABASE_NAME,
        collection=value.collection,
        query=value.query,
        projection=value.projection
      )
      display_member = value.display_member
      value_member = value.value_member
      lookup = load_sync(query)
      found = next((display_member(x) for x in lookup if value_member(x) == data), None)
      return found
    else:
      collection = value.collection
      if any(lookups) and collection:
        display_member = value.display_member
        value_member = value.value_member
        lookup = lookups[collection]['item_list']
        found = next((display_member(x) for x in lookup if value_member(x) == data), None)
        return found
      return data
  elif isinstance(value, (QuerySelectField)):
    for prop in value.query:
      if callable(value.query[prop]):
        value.query[prop] = value.query[prop](data)
    query = Query(
      database=DATABASE_NAME,
      collection=value.collection,
      query=value.query,
      projection=value.projection
    )
    display_member = value.display_member
    value_member = value.value_member
    lookup = load_sync(query)
    found = next((display_member(x) for x in lookup if value_member(x) == data), None)
    return found
  elif isinstance(value, (QuerySelectMultipleField)):
    for prop in value.query:
      if callable(value.query[prop]):
        value.query[prop] = value.query[prop](data)
    query = Query(
      database=DATABASE_NAME,
      collection=value.collection,
      query=value.query,
      projection=value.projection
    )
    display_member = value.display_member
    value_member = value.value_member
    lookup = load_sync(query)
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
    self.env.add_extension(RenderTableTag)
    self.env.filters.update({
      'escape': escape,
      'find_in': find_in,
      'from_json': from_json,
      'has_attr': has_attr,
      'is_datetime': is_datetime,
      'is_fieldlist': is_fieldlist,
      'is_hiddenfield': is_hiddenfield,
      'is_list': is_list,
      'is_currency_field': is_currency_field,
      'is_form_field': is_form_field,
      'is_lookup_select_field': is_lookup_select_field,
      'is_query_select_field': is_query_select_field,
      'is_key_value_form': is_key_value_form,
      'contains': contains,
      'endswith': endswith,
      'startswith': startswith,
      'to_field_list_label': to_field_list_label,
      'to_number_format': to_number_format,
      'to_float_format': to_float_format,
      'to_currency': to_currency,
      'to_current_date': to_current_date,
      'to_params': to_params,
      'to_phone_number': to_phone_number,
      'to_proper_case': to_proper_case,
      'to_string': to_string,
      'to_date': to_date,
      'to_date_time': to_date_time,
      'to_date_format': to_date_format,
      'db_lookup': db_lookup,
      'get_value': get_value,
      'dot': dot,
      'walk_dot': walk_dot,
      'walk_dot_form': walk_dot_form,
    })
    self.env.tests['escape'] = escape
    self.env.tests['find_in'] = find_in
    self.env.tests['from_json'] = from_json
    self.env.tests['has_attr'] = has_attr
    self.env.tests['is_datetime'] = is_datetime
    self.env.tests['is_fieldlist'] = is_fieldlist
    self.env.tests['is_hiddenfield'] = is_hiddenfield
    self.env.tests['is_list'] = is_list    
    self.env.tests['is_currency_field'] = is_currency_field
    self.env.tests['is_form_field'] = is_form_field
    self.env.tests['is_lookup_select_field'] = is_lookup_select_field
    self.env.tests['is_query_select_field'] = is_query_select_field
    self.env.tests['is_key_value_form'] = is_key_value_form
    self.env.tests['contains'] = contains
    self.env.tests['endswith'] = endswith
    self.env.tests['startswith'] = startswith
    self.env.tests['to_field_list_label'] = to_field_list_label
    self.env.tests['to_number_format'] = to_number_format
    self.env.tests['to_float_format'] = to_float_format
    self.env.tests['to_currency'] = to_currency
    self.env.tests['to_current_date'] = to_current_date
    self.env.tests['to_params'] = to_params
    self.env.tests['to_phone_number'] = to_phone_number
    self.env.tests['to_proper_case'] = to_proper_case
    self.env.tests['to_string'] = to_string
    self.env.tests['to_date'] = to_date
    self.env.tests['to_date_time'] = to_date_time
    self.env.tests['to_date_format'] = to_date_format
    self.env.tests['db_lookup'] = db_lookup
    self.env.tests['get_value'] = get_value
    self.env.tests['dot'] = dot
    self.env.tests['walk_dot'] = walk_dot
    self.env.tests['walk_dot_form'] = walk_dot_form


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


class RenderTableTag(StandaloneTag):
  tags = {'RenderTable'}

  def render(self, view, form, data):
    # Usage:
    #   {% RenderTable view=view, form=form, data=data %}
    items = view.list_layout['field_list']

    parts = []
    table_start = '''
      <table class="min-w-full divide-y divide-gray-200 shadow-md"
        hx-indicator=".htmx-indicator">
    '''
    table_end = '''
      </table>
    '''
    thead_start = '''
      <thead class="bg-gray-50">
        <tr>
    '''
    thead_end = '''
        </tr>
      </thead>
    '''
    thead_col_start = '''
      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
    '''
    thead_col_end = '''
      </th>
    '''
    thead_col_actions = '''
      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>  
    '''
    tbody_start = '''
      <tbody class="bg-white divide-y divide-gray-200">
    '''
    tbody_end = '''
      </tbody>
    '''
    tbody_row_start = '''
      <tr class="intro-y">    
    '''
    tbody_row_end = '''
      </tr>
    '''
    tbody_col_start = '''
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    '''
    tbody_col_end = '''
      </td>
    '''
    tbody_col_actions = f'''
      <td class="flex justify-between px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <a class="cursor-pointer" 
          hx-get="/{view.model_name}/{{ object['_id'] }}" 
          hx-target="#viewport" 
          hx-swap="innerHTML" 
          hx-push-url="true" 
          hx-indicator="#content-loader">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
          </svg>
        </a> 
        <a class="cursor-pointer"
          hx-get="/{view.model_name}/{{ object['_id'] }}/delete" 
          hx-target="#viewport" 
          hx-swap="innerHTML" 
          hx-push-url="true" 
          hx-indicator="#content-loader">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </a>
      </td>    
    '''
    template = '''
    <table class="min-w-full divide-y divide-gray-200 shadow-md"
      hx-indicator=".htmx-indicator">
      <thead class="bg-gray-50">
        <tr>
          {% for item in items %}
            {% set field = form[item] %}
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {{ field.label.text }}
            </th>
          {% endfor %}
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>        
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {% for object in data %}
          <tr class="intro-y">
            {% for item in items %}
              {% set field = form[item] %}
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {% if object[field.name]|is_datetime %}
                  {{ object[field.name]|to_date }}
                {% elif object[field.name]|is_list or field|is_query_select_field %}
                  {{ field|db_lookup(data=object[field.name]) }}
                {% else %}
                  {{ object[field.name] }}
                {% endif %}
              </td>
            {% endfor %}
            <td class="flex justify-between px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <a class="cursor-pointer" 
                hx-get="/{{ view.model_name }}/{{ object['_id'] }}" 
                hx-target="#viewport" 
                hx-swap="innerHTML" 
                hx-push-url="true" 
                hx-indicator="#content-loader">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                </svg>
              </a> 
              <a class="cursor-pointer"
                hx-get="/{{ view.model_name }}/{{ object['_id'] }}/delete" 
                hx-target="#viewport" 
                hx-swap="innerHTML" 
                hx-push-url="true" 
                hx-indicator="#content-loader">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </a>
            </td>
          </tr>
        {% else %}
          <tr class="intro-y">
            <td colspan="100%" class="px-6 py-4 text-center h-36">
              No Data
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>  
    
    '''

    parts.append(table_start)
    parts.append(thead_start)
    for item in items:
      field = form[item]
      parts.append(thead_col_start)
      parts.append(field.label.text)
      parts.append(thead_col_end)
    parts.append(thead_col_actions)
    parts.append(thead_end)
    parts.append(tbody_start)
    for object in data:
      parts.append(tbody_row_start)
      for item in items:
        field = form[item]
        parts.append(tbody_col_start)
        if isinstance(object[field.name], datetime.datetime):
          parts.append(object[field.name].strftime('%m/%d/%Y'))
        elif isinstance(object[field.name], list) or isinstance(field, QuerySelectField):
          parts.append(db_lookup(field, data=object[field.name]))
        else:
          val = str(object[field.name])
          parts.append(val)
        parts.append(tbody_col_end)
      parts.append(tbody_col_actions)
      parts.append(tbody_row_end)
    parts.append(tbody_end)
    parts.append(table_end)

    result = ''.join(parts)
    return result


def register_tags(templates):
  templates.env.add_extension(RenderColTag)
  templates.env.add_extension(RenderTableTag)

def configure_templates(directory='templates'):
  global templates
  templates = CustomJinja2Templates(directory=directory)
  register_tags(templates)
  return templates


def render_markup(markup: str = '', context: dict = {}):
  import os
  from pathlib import Path
  from jinja2 import Environment, BaseLoader, DictLoader
  from urllib.parse import quote, unquote
  from mango.template_utils.utils import (
    find_in,
    from_json,
    has_attr,
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
    to_date_time,
    to_date_format,
    to_currency,
    to_current_date,
    db_lookup,
    get_value,
    dot,
    walk_dot,
    walk_dot_form
  )

  # env = Environment(loader=DictLoader())
  env = Environment(loader=BaseLoader())

  env.filters.update({
    'find_in': find_in,
    'from_json': from_json,
    'has_attr': has_attr,
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
    'to_date_time': to_date_time,
    'to_date_format': to_date_format,
    'to_number_format': to_number_format,
    'to_float_format': to_float_format,
    'to_currency': to_currency,
    'to_current_date': to_current_date,
    'db_lookup': db_lookup,
    'get_value': get_value,
    'dot': dot,
    'walk_dot': walk_dot,
    'walk_dot_form': walk_dot_form,
  })
  env.tests['find_in'] = find_in
  env.tests['from_json'] = from_json
  env.tests['has_attr'] = has_attr
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
  env.tests['to_date_time'] = to_date_time
  env.tests['to_date_format'] = to_date_format
  env.tests['to_number_format'] = to_number_format
  env.tests['to_float_format'] = to_float_format
  env.tests['to_currency'] = to_currency
  env.tests['to_current_date'] = to_current_date
  env.tests['db_lookup'] = db_lookup
  env.tests['get_value'] = get_value
  env.tests['dot'] = dot    
  env.tests['walk_dot'] = walk_dot    
  env.tests['walk_dot_form'] = walk_dot_form

  markup = unquote(markup)
  tmpl = env.from_string(markup)

  content_rendered = tmpl.render(**context)
  return content_rendered
