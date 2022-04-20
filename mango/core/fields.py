from dotenv import load_dotenv
load_dotenv()
import os
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
from mango.db.rest import find, find_one, run_pipeline, find_sync, find_one_sync
from mango.db.models import Query, QueryOne
from mango.core.constants import label_class, input_class, textarea_class, chk_class, select_class, select_multiple_class, toggle_radio_class, toggle_switch_class
from mango.core.widgets import ToggleRadioWidget, ToggleSwitchWidget

DATABASE_NAME = os.environ.get('DATABASE_NAME')


class IntegerField2(IntegerField):
  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(IntegerField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class


class FloatField2(FloatField):
  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(FloatField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class


class EmailField2(EmailField):
  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(EmailField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class


class StringField2(StringField):
  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(StringField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class


class TextAreaField2(TextAreaField):
  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(TextAreaField2, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class


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
    **kwargs,
  ):
    super().__init__(unbound_field, label, validators, min_entries=min_entries, max_entries=max_entries, separator=separator, default=default, **kwargs)
    self.wrapper_class = wrapper_class

  def get_form_name(self):
    if issubclass(self.unbound_field.field_class, FormField):
      module_name = self.unbound_field.args[0].__module__
      name = self.unbound_field.args[0].__name__
    else:
      module_name = self.unbound_field.field_class.__module__
      name = self.unbound_field.field_class.__name__
    return f'{module_name}.{name}'


class DivField(Field):

  def __call__(self, **kwargs):
    return markupsafe.Markup(f'''
<div class="mt-2">
  <div class="mt-2 flex gap-4">
    <select class="flex-1 {select_class}">
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
    <select class="flex-1 {select_class}">
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
    <label class="inline-flex items-center">
      <input type="checkbox" class="form-checkbox {chk_class}" name="sun" value="">
      <span class="xml-2">Sun</span>
    </label>
    <label class="inline-flex items-center ml-4">
      <input type="checkbox" class="form-checkbox {chk_class}" name="mon" value="">
      <span class="xml-2">Mon</span>
    </label>
    <label class="inline-flex items-center ml-4">
      <input type="checkbox" class="form-checkbox {chk_class}" name="tue" value="">
      <span class="xml-2">Tue</span>
    </label>
    <label class="inline-flex items-center ml-4">
      <input type="checkbox" class="form-checkbox {chk_class}" name="wed" value="">
      <span class="xml-2">Wed</span>
    </label>
    <label class="inline-flex items-center ml-4">
      <input type="checkbox" class="form-checkbox {chk_class}" name="thu" value="">
      <span class="xml-2">Thu</span>
    </label>
    <label class="inline-flex items-center ml-4">
      <input type="checkbox" class="form-checkbox {chk_class}" name="fri" value="">
      <span class="xml-2">Fri</span>
    </label>
    <label class="inline-flex items-center ml-4">
      <input type="checkbox" class="form-checkbox {chk_class}" name="sat" value="">
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


class LookupSelectField(SelectField):
  widget = widgets.Select()
  
  def __init__(
    self,
    label=None,
    validators=None,
    coerce=str,
    choices=None,
    validate_choice=True,
    allow_blank=False,
    blank_text='Choose...',
    collection='lookup', 
    query={}, 
    projection={'label': 1, 'name': 1, 'item_list': 1}, 
    sort={}, 
    display_member=lambda data: f'{data.get("key")}', 
    value_member=lambda data: f'{data.get("value")}',
    wrapper_class='',
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce
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

  def get_choices(self, data):
    for prop in self.query:
      if callable(self.query[prop]):
        self.db_query.query[prop] = self.query[prop](data)
    
    blank_choice = None
    raw = find_one_sync(self.db_query)
    if self.allow_blank:
      blank_choice = [('', self.blank_text)]
    choices = [(self.value_member(x), self.display_member(x)) for x in raw['item_list']]
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
    allow_blank=False,
    blank_text='Choose...',
    collection=None, 
    query={}, 
    projection={'name': 1, 'value': 1},
    sort={}, 
    display_member=lambda data: f'{data.get("name")}', 
    value_member=lambda data: f'{data.get("value")}',
    wrapper_class='',
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce
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
    collection=None, 
    query={}, 
    projection={'name': 1, 'value': 1}, 
    sort={}, 
    display_member=lambda data: f'{data.get("name")}', 
    value_member=lambda data: f'{data.get("value")}',     
    wrapper_class='',
    **kwargs,
  ):
    super().__init__(label, validators, **kwargs)
    self.coerce = coerce
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

  def get_choices(self, data):
    choices = []
    if data:
      for prop in self.query:
        if callable(self.query[prop]):
          self.db_query.query[prop] = self.query[prop](data)
            
      raw = find_sync(self.db_query)
      choices = [(self.value_member(x), self.display_member(x)) for x in raw]
      if choices is not None:
        choices = choices if isinstance(choices, dict) else list(choices)
      else:
        self.choices = None
    return choices


class ToggleRadioField(RadioField):
  widget = ToggleRadioWidget()

  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(ToggleRadioField, self).__init__(label, validators, **kwargs)
    self.wrapper_class = wrapper_class


class ToggleSwitchField(BooleanField):
  widget = ToggleSwitchWidget()

  def __init__(self, label='', validators=None, wrapper_class='', **kwargs):
    super(ToggleSwitchField, self).__init__(label, validators, **kwargs)    
    self.wrapper_class = wrapper_class


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

