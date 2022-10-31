from dotenv import load_dotenv
load_dotenv()
import json, os
import asyncio
import markupsafe
from pydantic import ValidationError
from wtforms import (
  BooleanField,
  DateField,
  DateTimeField,
  DecimalField,
  EmailField,
  FileField,
  MultipleFileField,
  FloatField,
  IntegerField,
  RadioField,
  SelectField,
  SelectFieldBase,
  SelectMultipleField,
  StringField,
  SubmitField,
  HiddenField,
  PasswordField,
  TextAreaField,
  FormField,
  Field,
  FieldList,
  Form,
  widgets,
)
from wtforms_components import ColorField
from wtforms.utils import unset_value
from mango.db.rest import find, find_one, run_pipeline, find_sync, find_one_sync
from mango.db.models import Query, QueryOne
from mango.core.constants import label_class, input_class, textarea_class, chk_class, select_class, select_multiple_class, toggle_radio_class, toggle_switch_class
from mango.core.widgets import CodeMirrorWidget, DatalistWidget, ToggleRadioWidget, ToggleSwitchWidget, CurrencyWidget

DATABASE_NAME = os.environ.get('DATABASE_NAME')


class ColorField2(ColorField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(ColorField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

  def process_formdata(self, valuelist):
    if valuelist:
      if valuelist[0] == u'' or valuelist[0] == '':
        self.data = None
      else:
        self.data = valuelist[0]


# class CurrencyField(DecimalField):
#   def __init__(self, label=None, validators=None, places=unset_value, rounding=None, wrapper_class='', render_in_table=True, **kwargs):
#     super(CurrencyField, self).__init__(label, validators, **kwargs)    
#     self.wrapper_class = wrapper_class
#     self.render_in_table = render_in_table

#   def process_formdata(self, valuelist):
#     if len(valuelist) == 1:
#       self.data = [valuelist[0].strip('$').replace(',', '')]
#     else:
#       self.data = []

#     # Calls "process_formdata" on the parent types of "CurrencyField",
#     # which includes "DecimalField"
#     super(CurrencyField).process_formdata(self.data)


class BooleanField2(BooleanField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(BooleanField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class IntegerField2(IntegerField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(IntegerField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class CurrencyField(FloatField):
  widget = CurrencyWidget()

  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(CurrencyField, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class FloatField2(FloatField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(FloatField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class DateField2(DateField):
  def __init__(self, label='', validators=None, format="%Y-%m-%d", wrapper_class='', render_in_table=True, **kwargs):
    super(DateField2, self).__init__(label, validators, format="%Y-%m-%d", **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class DateTimeField2(DateTimeField):
  def __init__(self, label='', validators=None, format="%Y-%m-%d", wrapper_class='', render_in_table=True, **kwargs):
    super(DateTimeField2, self).__init__(label, validators, format="%Y-%m-%d", **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class DecimalField2(DecimalField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(DecimalField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table



class EmailField2(EmailField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(EmailField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class HiddenField2(HiddenField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(HiddenField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class StringField2(StringField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(StringField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class TextAreaField2(TextAreaField):
  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(TextAreaField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class FieldList2(FieldList):
  def __init__(
    self,
    unbound_field,
    label=None,
    validators=None,
    min_entries=0,
    max_entries=None,
    separator='-',
    default=(),
    wrapper_class='',
    render_in_table=True,
    **kwargs,
  ):
    super().__init__(unbound_field, label, validators, min_entries=min_entries, max_entries=max_entries, separator=separator, default=default, **kwargs)
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

  def get_form_name(self):
    if issubclass(self.unbound_field.field_class, FormField):
      module_name = self.unbound_field.args[0].__module__
      name = self.unbound_field.args[0].__name__
    else:
      module_name = self.unbound_field.field_class.__module__
      name = self.unbound_field.field_class.__name__
    return f'{module_name}.{name}'


class OperatingHoursField(Field):

  def __call__(self, **kwargs):
    return markupsafe.Markup(f'''
<div class="mt-2">
  <div class="mt-2 flex gap-4">
    <select id="{self.name}-0-start_time"
      name="{self.name}-0-start_time"
      class="flex-1 {select_class}">
      <option value="12am">12:00 AM</option>
      <option value="1am">1:00 AM</option>
      <option value="2am">2:00 AM</option>
      <option value="3am">3:00 AM</option>
      <option value="4am">4:00 AM</option>
      <option value="5am">5:00 AM</option>
      <option value="6am">6:00 AM</option>
      <option value="6am">6:00 AM</option>
      <option value="7am">7:00 AM</option>
      <option value="8am" selected="true">8:00 AM</option>
      <option value="9am">9:00 AM</option>
      <option value="10am">10:00 AM</option>
      <option value="11am">11:00 AM</option>
    </select>
    <select id="{self.name}-0-end_time"
      name="{self.name}-0-end_time"
      class="flex-1 {select_class}">
      <option value="12pm">12:00 PM</option>
      <option value="1pm">1:00 PM</option>
      <option value="2pm">2:00 PM</option>
      <option value="3pm">3:00 PM</option>
      <option value="4pm">4:00 PM</option>
      <option value="5pm">5:00 PM</option>
      <option value="6pm">6:00 PM</option>
      <option value="6pm">6:00 PM</option>
      <option value="7pm">7:00 PM</option>
      <option value="8pm">8:00 PM</option>
      <option value="9pm">9:00 PM</option>
      <option value="10pm">10:00 PM</option>
      <option value="11pm">11:00 PM</option>    
    </select>
  </div>
  <div class="mt-2">
    <label for="{self.name}-0-sunday"
      class="inline-flex items-center">
      <input type="checkbox" 
        id="{self.name}-0-sunday"
        name="{self.name}-0-sunday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Sun</span>
    </label>
    <label for="{self.name}-0-monday"
      class="inline-flex items-center ml-4">
      <input type="checkbox"
        id="{self.name}-0-monday"
        name="{self.name}-0-monday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Mon</span>
    </label>
    <label for="{self.name}-0-tuesday"
      class="inline-flex items-center ml-4">
      <input type="checkbox"
        id="{self.name}-0-tuesday"
        name="{self.name}-0-tuesday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Tue</span>
    </label>
    <label for="{self.name}-0-wednesday"
      class="inline-flex items-center ml-4">
      <input type="checkbox"
        id="{self.name}-0-wednesday"
        name="{self.name}-0-wednesday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Wed</span>
    </label>
    <label for="{self.name}-0-thursday"
      class="inline-flex items-center ml-4">
      <input type="checkbox"
        id="{self.name}-0-thursday"
        name="{self.name}-0-thursday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Thu</span>
    </label>
    <label for="{self.name}-0-friday"
      class="inline-flex items-center ml-4">
      <input type="checkbox"
        id="{self.name}-0-friday"
        name="{self.name}-0-friday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Fri</span>
    </label>
    <label for="{self.name}-0-Saturday"
      class="inline-flex items-center ml-4">
      <input type="checkbox"
        id="{self.name}-0-Saturday"
        name="{self.name}-0-Saturday"
        class="form-checkbox {chk_class}">
      <span class="xml-2">Sat</span>
    </label>
  </div>
</div>
      ''')

  def _value(self):
    if self.data:
      return ', '.join(self.data)
    else:
      return ''

  def process_formdata(self, valuelist):
    if valuelist:
      self.data = [x.strip() for x in valuelist[0].split(',')]
    else:
      self.data = []


class DatalistField(StringField):
  """
  Custom field type for datalist input
  """
  widget = DatalistWidget()

  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, datalist=[], **kwargs):
    super(DatalistField, self).__init__(label, validators, **kwargs)
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table
    self.datalist = datalist

  def _value(self):
    if self.data:
      return u''.join(self.data)
    else:
      return u''


class LookupSelectField(SelectField):
  widget = widgets.Select()
  
  def __init__(
    self,
    label=None,
    validators=None,
    coerce=str,
    choices=None,
    validate_choice=True,
    serialize_choices=False,
    allow_blank=False,
    blank_text='Choose...',
    collection='lookup', 
    query={}, 
    projection={'label': 1, 'name': 1, 'item_list': 1}, 
    sort={}, 
    display_member=lambda data: f'{data.get("key")}', 
    value_member=lambda data: f'{data.get("value")}',
    wrapper_class='',
    render_in_table=True,
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce
    self.serialize_choices = serialize_choices
    self.allow_blank = allow_blank
    self.blank_text = blank_text
    self.collection = collection
    self.query = query
    self.db_query = QueryOne(
      database=DATABASE_NAME,
      collection=collection,
      query=query.copy(),
      projection=projection,
      sort=sort
    )
    self.projection = projection
    self.sort = sort
    self.display_member = display_member
    self.value_member = value_member
    self.validate_choice = validate_choice
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

  def get_choices(self, data):
    for prop in self.query:
      if callable(self.query[prop]):
        self.db_query.query[prop] = self.query[prop](data)
    
    blank_choice = None
    raw = find_one_sync(self.db_query)
    if self.allow_blank:
      blank_choice = [('', self.blank_text)]
    choices = [(self.value_member(x), self.display_member(x)) for x in sorted(raw['item_list'], key=lambda data: data['value'])]
    if blank_choice:
      return blank_choice + choices
    if choices is not None:
      choices = choices if isinstance(choices, dict) else list(choices)
    else:
      choices = None
    return choices


class PicklistSelectField(SelectField):
  widget = widgets.Select()
  
  def __init__(
    self,
    label=None,
    validators=None,
    coerce=str,
    choices=None,
    validate_choice=True,
    datalist=[],
    allow_blank=False,
    blank_text='Choose...',
    wrapper_class='',
    render_in_table=True,
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce
    self.datalist = datalist
    self.allow_blank = allow_blank
    self.blank_text = blank_text
    self.validate_choice = validate_choice
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

  def get_choices(self, data):
    blank_choice = None
    if self.allow_blank:
      blank_choice = [('', self.blank_text)]
    choices = [(x, x) for x in self.datalist]
    if blank_choice:
      return blank_choice + choices
    if choices is not None:
      choices = choices if isinstance(choices, dict) else list(choices)
    else:
      choices = None
    return choices


class QuerySelectField(SelectField):
  widget = widgets.Select()
  
  def __init__(
    self,
    label=None,
    validators=None,
    coerce=str,
    choices=None,
    validate_choice=True,
    serialize_choices=False,
    allow_blank=False,
    blank_text='Choose...',
    collection=None, 
    query={}, 
    projection={'name': 1, 'value': 1},
    sort={}, 
    display_member=lambda data: f'{data.get("name")}', 
    value_member=lambda data: f'{data.get("value")}',
    wrapper_class='',
    render_in_table=True,
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce
    self.serialize_choices = serialize_choices
    self.allow_blank = allow_blank
    self.blank_text = blank_text
    self.collection = collection
    self.query = query
    self.db_query = Query(
      database=DATABASE_NAME,
      collection=collection,
      query=query.copy(),
      projection=projection,
      sort=sort
    )
    self.projection = projection
    self.sort = sort
    self.display_member = display_member
    self.value_member = value_member
    self.validate_choice = validate_choice
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

  def get_choices(self, data):
    for prop in self.query:
      if callable(self.query[prop]):
        self.db_query.query[prop] = self.query[prop](data)
    
    blank_choice = None
    raw = find_sync(self.db_query)
    if self.allow_blank:
      blank_choice = [('', self.blank_text)]
    choices = [(self.value_member(x), self.display_member(x)) for x in raw]
    if blank_choice:
      return blank_choice + choices
    if choices is not None:
      choices = choices if isinstance(choices, dict) else list(choices)
    else:
      choices = None
    return choices


class QuerySelectMultipleField(SelectMultipleField):
  widget = widgets.Select(multiple=True)
  
  def __init__(
    self,
    label=None,
    validators=None,
    coerce=str,
    choices=None,
    validate_choice=True,
    serialize_choices=False,
    collection=None, 
    query={}, 
    projection={'name': 1, 'value': 1}, 
    sort={}, 
    display_member=lambda data: f'{data.get("name")}', 
    value_member=lambda data: f'{data.get("value")}',     
    wrapper_class='',
    render_in_table=True,
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce    
    self.serialize_choices = serialize_choices
    self.collection = collection
    self.query = query
    self.db_query = Query(
      database=DATABASE_NAME,
      collection=collection,
      query=query.copy(),
      projection=projection,
      sort=sort
    )
    self.projection = projection
    self.sort = sort
    self.display_member = display_member
    self.value_member = value_member
    self.validate_choice = validate_choice
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

  def get_choices(self, data):
    choices = []
    for prop in self.query:
      if callable(self.query[prop]):
        if data: 
          self.db_query.query[prop] = self.query[prop](data)
        else:
          return []
            
    raw = find_sync(self.db_query)
    choices = [(self.value_member(x), self.display_member(x)) for x in raw]
    if choices is not None:
      choices = choices if isinstance(choices, dict) else list(choices)
    else:
      self.choices = None
    return choices


class ToggleRadioField(RadioField):
  widget = ToggleRadioWidget()

  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(ToggleRadioField, self).__init__(label, validators, **kwargs)
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class ToggleSwitchField(BooleanField):
  widget = ToggleSwitchWidget()

  def __init__(self, label='', validators=None, wrapper_class='', render_in_table=True, **kwargs):
    super(ToggleSwitchField, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table


class WeeklyHoursField(Field):
  widget = widgets.WeekInput()

  def _value(self):
      if self.data:
          return ', '.join(self.data)
      else:
          return ''

  def process_formdata(self, valuelist):
      if valuelist:
          self.data = [x.strip() for x in valuelist[0].split(',')]
      else:
          self.data = []


class CodeMirrorField(TextAreaField):
  """Code Mirror Field
  A TextAreaField with a custom widget
  :param language: CodeMirror mode
  :param config: CodeMirror config
  """
  def __init__(self, label='', validators=None, config=None, wrapper_class='', render_in_table=True, **kwargs):
    widget = CodeMirrorWidget(config)
    super(CodeMirrorField, self).__init__(label=label, validators=validators, widget=widget, **kwargs)
    self.config = config
    self.wrapper_class = wrapper_class
    self.render_in_table = render_in_table

    