import asyncio
import json
import markupsafe
from typing import List
from wtforms import Form, BooleanField, RadioField, SelectField, SelectFieldBase, widgets
from wtforms.fields import StringField
from wtforms.widgets import Select, TextInput
from wtforms.fields.core import Field, UnboundField
from mango.db.api import find, find_one, run_pipeline, find_sync
from mango.db.models import Query
from mango.core.widgets import TagsWidget, ToggleRadioWidget, ToggleSwitchWidget
# from mango.utils.utils import settings
from settings import templates, DATABASE_NAME


label_class = 'block text-gray-700 text-sm font-light mb-2'
input_class = '''
  form-control
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none
'''
textarea_class = '''
  form-control
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  h-48
  focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none
'''
chk_class = '''
  form-check-input
  xappearance-none
  h-4
  w-4
  border
  border-gray-300
  rounded-sm
  bg-white
  checked:bg-blue-600
  checked:border-blue-600
  focus:outline-none
  transition
  duration-200
  mt-1
  align-top
  bg-no-repeat
  bg-center
  bg-contain
  float-left
  mr-2
  cursor-pointer
'''
select_class = '''form-select appearance-none
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding bg-no-repeat
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none'''
multi_select_class = '''
  form-control
  block
  w-full
  px-2
  py-0.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none
'''
toggle_radio_class = '''
  w-full
  transition
  ease-in-out
  focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none
  toggle-radio
'''
toggle_switch_class = '''
  toggle-switch-container
  cursor-pointer
'''


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


class TagListField(Field):
  widget = TextInput()

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

  # def __init__(self, label=None, validators=None, filters=tuple(),
  #   description='', id=None, default=None, widget=None,
  #   render_kw=None, _form=None, _name=None, _prefix='',
  #   _translations=None, _meta=None):
  #   super(WeeklyHoursField, self).__init__(label, validators, **kwargs)                 
  # def __html__(self):
  #       """
  #       Returns a HTML representation of the field. For more powerful rendering,
  #       see the :meth:`__call__` method.
  #       """
  #       return '''
  #       <ul>
  #         <li>Sun</li>
  #         <li>Mon</li>
  #         <li>Tue</li>
  #         <li>Wed</li>
  #         <li>Thu</li>
  #         <li>Fri</li>
  #         <li>Sat</li>
  #       </ul>
  #       '''


class QuerySelectField(SelectFieldBase):
  widget = widgets.Select()

  def __init__(self, label=None, validators=None, 
               collection=None, query_type='find', query={},
               projection={'name': 1, 'value': 1, '_id': 0}, 
               allow_blank=True, blank_text='Choose...', 
               display_member=lambda data: f'{data.get("name")}', value_member=lambda data: f'{data.get("value")}', **kwargs):
    super(QuerySelectField, self).__init__(label, validators, **kwargs)

    self.collection = collection
    self.query =  Query(
      database=DATABASE_NAME,
      collection=collection,
      query_type=query_type,
      query=query,
      projection=projection
    )
    self.allow_blank = allow_blank
    self.blank_text = blank_text
    self.display_member = display_member
    self.value_member = value_member
    self._object_list = None

  def _get_data(self):
    if self._formdata is not None:
      for pk, obj in self._get_object_list():
        if pk == self._formdata:
          self._set_data(obj)
          break
    return self._data

  def _set_data(self, data):
    self._data = data
    self._formdata = None

  data = property(_get_data, _set_data)

  def _get_object_list(self):
    if self._object_list is None:
      self._object_list = self.load_choices()

    return self._object_list

  def iter_choices(self):
    if self.allow_blank:
      yield (None, self.blank_text, self.data is None)

    for x in self._get_object_list():
      yield (self.value_member(x), self.display_member(x), self.value_member(x) == self.data)
      # yield x  # TODO: Remove

  def load_choices(self):
    choices = find_sync(self.query)
    # results = find_sync(self.query)  # TODO: Remove
    # choices = [(v, v, v == self.data) for x in results for k, v in x.items() if k == 'value']  # TODO: Remove
    return choices


class TagsField(SelectField):
    """Stringfield for a list of separated tags"""

    widget = TagsWidget()

    def __init__(self, label='', validators=None, remove_duplicates=True, to_lowercase=True, separator=' ', **kwargs):
        """
        Construct a new field.
        :param label: The label of the field.
        :param validators: A sequence of validators to call when validate is called.
        :param remove_duplicates: Remove duplicates in a case insensitive manner.
        :param to_lowercase: Cast all values to lowercase.
        :param separator: The separator that splits the individual tags.
        """
        super(TagsField, self).__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.to_lowercase = to_lowercase
        self.separator = separator
        self.data = []

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def pre_validate(self, form):
        pass 

    def process_formdata(self, valuelist):
        if valuelist:
          if len(valuelist) > 1:
            self.data = [x.strip() for x in valuelist]
          else:
            self.data = [x.strip() for x in valuelist[0].split(self.separator)]
          if self.remove_duplicates:
              self.data = list(self._remove_duplicates(self.data))
          if self.to_lowercase:
              self.data = [x.lower() for x in self.data]

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving manner"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item


class ToggleRadioField(RadioField):
  widget = ToggleRadioWidget()

  def __init__(self, label='', validators=None, **kwargs):
    super(ToggleRadioField, self).__init__(label, validators, **kwargs)


class ToggleSwitchField(BooleanField):
  widget = ToggleSwitchWidget()

  def __init__(self, label='', validators=None, **kwargs):
    super(ToggleSwitchField, self).__init__(label, validators, **kwargs)