from email.policy import default
from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
from wtforms import (
  # BooleanField,
  DateField,
  DateTimeField,
  DecimalField,
  EmailField,
  FileField,
  MultipleFileField,
  FloatField,
  #IntegerField,
  RadioField,
  SelectField,
  SelectMultipleField,
  # StringField,
  SubmitField,
  HiddenField,
  PasswordField,
  # TextAreaField,
  FormField,
  # FieldList,
  Form,
)
from wtforms.validators	import DataRequired, AnyOf, NoneOf
from mango.core.fields import DatalistField, LookupSelectField, QuerySelectField, QuerySelectMultipleField, ToggleSwitchField
from mango.core.fields import (
  BooleanField2 as BooleanField,
  IntegerField2 as IntegerField,
  StringField2 as StringField,
  TextAreaField2 as TextAreaField,
  FieldList2 as FieldList
)
from mango.core.constants import chk_class, input_class, label_class, select_class, select_multiple_class, textarea_class, toggle_radio_class, toggle_switch_class, hs_element_type, hs_config_tom_select, hs_field_type, hs_field_type_form_field
from mango.core.choices import DATA_TYPES, FIELD_TYPES
from mango.core.validators import DataRequiredIf, OptionalIfFieldEqualTo


def get_class(class_str: str):
  from importlib import import_module
  try:
    module_path, class_name = class_str.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)
  except (ImportError, AttributeError) as e:
    raise ImportError(class_str)

def get_string_form(prefix: str):
  class StaticForm(Form):
    pass

  setattr(
    StaticForm, 
    prefix, 
    StringField(
      'StringField',
      validators= [DataRequired()],
      render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    )
  )
  result = StaticForm()
  return result

def get_dynamic_form(form_name: str, prefix: str):
  class DynamicForm(Form):
    pass

  _, class_name = form_name.rsplit('.', 1)

  field_class = get_class(form_name)
  form_field = field_class(prefix, render_kw={})
  # form_field = field_class(prefix=prefix)
  
  setattr(
    DynamicForm, 
    prefix,
    form_field
  )
  result = DynamicForm()
  return result


class KeyValueForm(Form):
  key = StringField(
    'Key',
    # validators= [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    default = '',
  )
  value = StringField(
    'Value',
    # validators= [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    default = '',
  )
  use_quotes = BooleanField(
    'Use Quotes?',
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    default = True,
  )
  form_mode = LookupSelectField(
    'Form Mode',
    collection = 'lookup',
    query = { 'name': 'form_mode' },
    render_kw = {},
    default = 'both',    
  )


class ParameterForm(Form):
  label = StringField(
    'Label', 
    render_kw = {
      'class' : input_class,
      # 'data-script': 'on input copyToLowerSnake(me, "name") end',
    },
  )
  name = StringField(
    'API Name', 
    render_kw = {
      'class' : input_class,
    },
  )
  data_type = LookupSelectField(
    'Data Type',
    allow_blank = True,
    blank_text = 'Pick...',
    collection = 'lookup',
    query = { 'name': 'data_type' },
  )
  value = StringField(
    'Value', 
    render_kw = {
      'class' : input_class,
    },
  )
  is_visible = ToggleSwitchField(
    'Is Visible?', 
    render_kw = {
      'class' : chk_class,
    },
  )


class SpacingForm(Form):
  top = StringField(
    'Top', 
    render_kw = {
      'class' : input_class,
    },
  )
  bottom = StringField(
    'Bottom', 
    render_kw = {
      'class' : input_class,
    },
  )
  left = StringField(
    'Left', 
    render_kw = {
      'class' : input_class,
    },
  )
  right = StringField(
    'Right', 
    render_kw = {
      'class' : input_class,
    },
  )


class ActionForm(StarletteForm):
  topic = StringField(
    'Topic', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'install HandleValidity end on input toLowerUri(me) end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class RoleForm(StarletteForm):
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )  
  # current_action = QuerySelectField(
  #   'Current Action',
  #   collection = 'action', 
  #   projection = { 'topic': 1 }, 
  #   display_member = lambda data: f'{data["topic"]}', 
  #   value_member = lambda data: f'{data["_id"]}',
  #   render_kw = { 'class': select_class, 'data-script': 'install HandleValidity end' },
  # )
  # action_date = DateField(
  #   'Action Date', 
  #   render_kw = { 'class': input_class, 'data-type': 'datetime' },
  # )
  action_list = QuerySelectMultipleField(
    'Actions',
    collection = 'action', 
    projection = { 'topic': 1 }, 
    display_member = lambda data: f'{data["topic"]}', 
    value_member = lambda data: f'{data["topic"]}',
    render_kw = { 'class': select_multiple_class, 'data-script': hs_config_tom_select },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )

  def validate_current_action(form, field):
    if field.data == '__None':
      field.data = None

  def validate_action_list(form, field):
    if field.data == None:
      field.data = []


class ModelForm(StarletteForm):
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  label_plural = StringField(
    'Plural Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  to_string = StringField(
    'To String',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  order_by = QuerySelectMultipleField(
    'Order By',
    collection = 'model_field', 
    query = { 'model_name': lambda data: data["name"] },
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
    wrapper_class = 'flex-1',
  )
  page_size = IntegerField(
    'Page Size',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  field_order = QuerySelectMultipleField(
    'Field Order',
    collection = 'model_field', 
    query = { 'model_name': lambda data: data["name"] },
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
    wrapper_class = 'flex-1',
  )
  is_custom = ToggleSwitchField(
    'Is Custom?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class ModelRecordTypeForm(StarletteForm):
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class ModelFieldForm(StarletteForm):
  model_name = QuerySelectField(
    'Model',
    collection = 'model', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'pattern': 'myvalue', 'class': select_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators=[DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  data_type = QuerySelectField(
    'Data Type', 
    collection = 'data_type', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()],
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'class': select_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_optional = ToggleSwitchField(
    'Is Optional?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = '',
  )
  is_list = ToggleSwitchField(
    'Is List?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = '',
  )
  default_value = StringField(
    'Default Value',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  default_value_use_quotes = ToggleSwitchField(
    'Default Value Use Quotes?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = '',
  )
  field_type = QuerySelectField(
    'Field Type', 
    collection = 'field_type', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()],
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'class': select_class, 'data-script': f'install HandleValidity end {hs_field_type}', 'data-script2': hs_field_type },
    wrapper_class = 'flex-1',
  )
  field_type_form_field = StringField(
    'Field Type Form Field',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  placeholder_field = StringField(
    'Placeholder Field',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  validator_list = FieldList(
    StringField(
      'Validator',
      render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    ),
    min_entries=0,
    wrapper_class = 'flex-1',
  )
  attribute_list = FieldList(
    FormField(KeyValueForm),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  collection = StringField(
    'Collection',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  projection_list = FieldList(
    FormField(KeyValueForm),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  query_list = FieldList(
    FormField(KeyValueForm),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  order_by_list = FieldList(
    FormField(KeyValueForm),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  display_member = StringField(
    'Display Member',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  value_member = StringField(
    'Value Member',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  allow_blank = ToggleSwitchField(
    'Allow Blank?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end on load set elt to first <input/> in me toggleElementHidden(elt, "checked", "wrapper_blank_text", false) end on change set elt to first <input/> in me toggleElementHidden(elt, "checked", "wrapper_blank_text", false) end' },
    wrapper_class = '',
  )
  blank_text = StringField(
    'Blank Text',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )

  # def __init__(self, request: StarletteRequest, *args, **kwargs):
  #   self.allow_blank.wrapper_class = 'test-class'
  #   super().__init__(request=request, args=args, kwargs=kwargs)



'''
  TODO: Need to support HandleValidity for the LayoutForm and LayoutLevel[x]Form classes
'''

class LayoutLevel4Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
    wrapper_class = 'flex-1',
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )


class LayoutLevel3Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
    wrapper_class = 'flex-1',
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  items = FieldList(
    FormField(LayoutLevel4Form),
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )


class LayoutLevel2Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
    wrapper_class = 'flex-1',
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  items = FieldList(
    FormField(LayoutLevel3Form),
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )


class LayoutLevel1Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
    wrapper_class = 'flex-1',
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  items = FieldList(
    FormField(LayoutLevel2Form),
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )


class LayoutForm(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
    wrapper_class = 'flex-1',
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )
  items = FieldList(
    FormField(LayoutLevel1Form),
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )


class PageLayoutForm(StarletteForm):
  model_name = QuerySelectField(
    'Model', 
    collection = 'model', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  model_record_type = QuerySelectField(
    'Model Record Type', 
    collection = 'model_record_type', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired('label')],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  element_list = FieldList(
    StringField(
      'Element',
      render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    ),
    wrapper_class = 'flex-1',
  )
  field_list = FieldList(
    FormField(ModelFieldForm),
    wrapper_class = 'flex-1',
  )
  related_list = QuerySelectMultipleField(
    'Related List',
    collection = 'model', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': f'install HandleValidity end {hs_config_tom_select}' },
    wrapper_class = 'flex-1',
  )
  role_list = QuerySelectMultipleField(
    'Roles',
    collection = 'role', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': f'install HandleValidity end {hs_config_tom_select}' },
    wrapper_class = 'flex-1',
  )
  items = FieldList(
    FormField(LayoutForm),
    wrapper_class = 'flex-1',
  )
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )

  # def list_layout(self):
  #   return [
  #     'model_name',
  #     'model_record_type',
  #     'label',
  #     'name',
  #     'is_default',
  #   ]


class ListLayoutForm(StarletteForm):
  model_name = QuerySelectField(
    'Model', 
    collection = 'model', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 
      'autofocus': 'true', 
      'class': select_class, 
      'data-script': 'install HandleValidity end on htmx:afterOnLoad configTomSelect("#field_list") end',
      'hx-trigger': 'change',
      'hx-push-url': 'false',
      'hx-param': 'none',
      'hx-vals': 'js:{filter_key: "model_name", filter_value: event.target.value}',
      'hx-get': '/select-options/model_field',
      'hx-target': '#field_list',
    },
    wrapper_class = 'flex-1',
  )
  model_record_type = QuerySelectField(
    'Model Record Type', 
    collection = 'model_record_type', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired('label')],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  field_list = QuerySelectMultipleField(
    'Field List',
    collection = 'model_field', 
    query = { 'model_name': lambda data: data["model_name"] },
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    render_kw = { 'class': select_class, 'data-script': f'install HandleValidity end {hs_config_tom_select}' },
    wrapper_class = 'flex-1',
  )
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class TabForm(StarletteForm):
  model_name = QuerySelectField(
    'Model', 
    collection = 'model', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  sequence = IntegerField(
    'Sequence', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class AppForm(StarletteForm):
  label = StringField(
    'Label', 
    validators=[DataRequired()],
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  description = StringField(
    'Description',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  logo = StringField(
    'Logo',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  tab_list = QuerySelectMultipleField(
    'Tabs',
    collection = 'tab', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': f'install HandleValidity end {hs_config_tom_select}' },
    wrapper_class = 'flex-1',
  )
  role_list = QuerySelectMultipleField(
    'Roles',
    collection = 'role', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': f'install HandleValidity end {hs_config_tom_select}' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class LookupForm(StarletteForm):
  label = StringField(
    'Label', 
    validators=[DataRequired()],
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  description = TextAreaField(
    'Description',
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  item_list = FieldList(
    FormField(KeyValueForm),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )


class PageElementForm(StarletteForm):
  label = StringField(
    'Label', 
    validators=[DataRequired()],
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'install HandleValidity end on input copyToLowerSnake(me, "name") end' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  description = TextAreaField(
    'Description',
    render_kw = { 'class': textarea_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  content = TextAreaField(
    'Content',
    render_kw = { 'class': textarea_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class, 'data-script': 'install HandleValidity end' },
    wrapper_class = 'flex-1',
  )
