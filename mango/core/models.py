'''
  Core Models

  Notes:
    All classes will use singular names.
    All database collections will be lowercase with underscores replacing spaces.
'''
import datetime
from enum import Enum
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, PositiveInt
from wtforms import Field


class KeyValue(BaseModel):
  key: str
  value: str


'''
  This class represents a given action to perform.
'''
class Action(BaseModel):
  topic: str # The authorized action to peform
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.topic

  def new_dict():
    return {'topic': '', 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'action'
    search_index_name = 'action_search'
    order_by = [
      'topic',
    ]
    page_size = 0


'''
  This class represents a given role with a collection of actions. Users must
  have the corresponding actions or roles in order to perform actions and behaviors.
'''
class Role(BaseModel):
  label: str
  name: str  # usually lowercase with underscores instead of spaces
  # current_action: Optional[str] = ''
  # action_date: Optional[datetime.datetime]
  action_list: List[str] = []  # list of authorized actions for the given role  
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label

  def new_dict():
    return {'label': '', 'name': '', 'action_list': [], 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'role'
    search_index_name = 'role_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  This class represents a single model definition. It is usually added to an App and can have
  multiple PageLayout definitions.
  Create GET|POST paths will use the naming convention: /<name>/create
  Update GET|POST paths will use the naming convention: /<name>/{id}
  Delete GET|POST paths will use the naming convention: /<name>/{id}/delete
  List GET paths will use the naming convention: /<name>
  All route shortcuts will use the naming convention: <name>-create|update|delete|list
  Atlas Search will use the naming convention: <name>_search
'''
class Model(BaseModel):
  label: str
  label_plural: str
  name: str  # usually lowercase with underscores instead of spaces
  to_string: str  # string for representing current object instance, e.g. f'{self.label}'
  order_by: List[str] = []  # holds the order sequence for sorting
  page_size: int = 0  # if zero, then no pagination
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label

  def new_dict():
    return {'label': '', 'label_plural': '', 'name': '', 'to_string': '', 'order_by': [], 'page_size': 0, 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'model'
    search_index_name = 'model_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  This class represents a record type for a given Model.
'''
class ModelRecordType(BaseModel):
  label: str
  name: str  # usually lowercase with underscores instead of spaces
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label

  def new_dict():
    return {'label': '', 'name': '', 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'model_record_type'
    search_index_name = 'model_record_type_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  This class represents a single field related to a given Model object.
  * Need to support SelectField with Choices, Validators, render_kw, Widgets, etc.
  * Need to support Field enclosers: FormField, FieldList, custom fields, etc.
'''
class ModelField(BaseModel):
  model_name: str
  label: str
  name: str  # usually lowercase with underscores instead of spaces
  data_type: str  # usually sourced from a List of tuples (value, label), e.g. str,int,bool
  is_optional: bool = False  # Indicates if this field is Optional
  is_list: bool = False  # Indicates if this field is List
  default_value: str = ''  # this should be coerced by the data_type entry, e.g. str should have quotes
  default_value_use_quotes: bool = True  # wrap the default with quotes (") if True
  field_type: str  # usually sourced from a list of valid WTForms element types
  validator_list: Optional[List[str]] = []
  attribute_list: Optional[List[KeyValue]] = []
  collection: str = ''  # collection to query
  projection_list: Optional[List[KeyValue]] = []  # fields to include in query
  query_list: Optional[List[KeyValue]] = []  # criteria for executing query
  order_by_list: Optional[List[KeyValue]] = []  # order criteria for query
  display_member: str = ''  # what to display in QuerySelect or QuerySelectMultiple
  value_member: str = ''  # what to store from QuerySelect or QuerySelectMultiple
  allow_blank: bool = False  # option to include a blank <option>
  blank_text: str = ''  # text to display for blank <option>
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label
  
  def new_dict():
    return {'model_id': '', 'label': '', 'name': '', 'data_type': '', 'default_value': '', 'default_value_use_quotes': True, 'field_type': '', 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'model_field'
    search_index_name = 'model_field_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  The Layout class represents the actual element layout for a given model.
'''
class Layout(BaseModel):
  element_type: str  # e.g. div, field
  field: Optional[str] = ''  # e.g. model_name, model_record_type
  css_class: Optional[str] = ''
  css_class_use_quotes: Optional[bool] = True
  inner_text: Optional[str] = ''  # e.g. Addess Info
  inner_html: Optional[str] = ''  # e.g. <span>Address Info</span>
  label_class: Optional[str] = ''
  label_class_use_quotes: Optional[bool] = True
  items: Optional[List['Layout']]
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.element_type
  
  def new_dict():
    return {'element_type': '', 'field': '', 'css_class': '', 'css_class_use_quotes': True, 'inner_text': '', 'inner_html': '', 'label_class': '', 'label_class_use_quotes': True, 'layout': []}

  class Meta:
    name = 'layout'
    search_index_name = 'layout_search'
    order_by = [
      'element_type',
    ]
    page_size = 0


'''
  The PageLayout class represents the page layout for a given Model object.
  There can only be one page_layout that is_default set to True.
  * Consider allowing a page layout to override the following for a given ModelField:
      ModelFieldAttribue
      ModelFieldChoice
      ModelFieldValidator
  * Consider how fields are laid out on a page.
'''
class PageLayout(BaseModel):
  model_name: str
  model_record_type: str  # holds the record type for the Model
  label: str
  name: str  # usually lowercase with underscores instead of spaces
  element_list: List = []  # holds a list of available HTML elements
  field_list: List[ModelField] = []  # holds a list of available fields by model_id
  related_list: List[Model] = []  # holds a list of related objects by model_id
  role_list: List[Role] = []  # loaded from the Roles collection
  items: List[Layout] = []  # holds the UI layout
  is_default: bool = False
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label
  
  def new_dict():
    return {'model_name': '', 'model_record_type': '', 'label': '', 'name': '', 'element_list': [], 'field_list': [], 'related_list': [], 'role_list': [], 'is_default': False, 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'page_layout'
    search_index_name = 'page_layout_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  The ListLayout class represents the list layout for a given Model object.
  There can only be one list_layout that is_default set to True.
'''
class ListLayout(BaseModel):
  model_name: str
  model_record_type: str  # holds the record type for the Model
  label: str
  name: str  # usually lowercase with underscores instead of spaces
  field_list: List[str] = []  # holds a list of available fields by name
  is_default: bool = False
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label
  
  def new_dict():
    return {'model_name': '', 'model_record_type': '', 'label': '', 'name': '', 'field_list': [], 'is_default': False, 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'list_layout'
    search_index_name = 'list_layout_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  This class represents navigation to a given Model object.
'''
class Tab(BaseModel):
  model_name: str  # references the a given Model object
  label: str  # this can override the Model label
  sequence: PositiveInt = 0  # used for ordering
  is_default: bool = False
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label

  def new_dict():
    return {'model_id': '', 'label': '', 'sequence': 0, 'is_default': False, 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'tab'
    search_index_name = 'tab_search'
    order_by = [
      'label',
    ]
    page_size = 0


'''
  This class represents a single application definition. It can contain multiple
  Models. This encapsulates all the tabs and navigation to Model and PageLayout objects.
'''
class App(BaseModel):
  label: str
  name: str  # usually lowercase with underscores instead of spaces
  description: str = ''
  logo: str = ''  # must be less than 20kb and 300px x 55px max size.
  tab_list: List[str] = []
  role_list: List[str] = []
  is_locked: bool = False
  is_active: bool = True

  def __str__(self):
    return self.label
  
  def new_dict():
    return {'label': '', 'name': '', 'description': '', 'logo': '', 'tab_list': [], 'role_list': [], 'is_locked': False, 'is_active': True}

  class Meta:
    name = 'app'
    search_index_name = 'app_search'
    order_by = [
      'label',
    ]
    page_size = 0
