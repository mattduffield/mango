from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
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
  SelectMultipleField,
  StringField,
  SubmitField,
  HiddenField,
  PasswordField,
  TextAreaField,
  FormField,
  FieldList,
  Form,
)
from wtforms.validators	import DataRequired, NoneOf
from mango.core.fields import QuerySelectField, QuerySelectMultipleField, ToggleSwitchField
from mango.core.constants import chk_class, input_class, label_class, select_class, select_multiple_class, textarea_class, toggle_radio_class, toggle_switch_class
from mango.core.choices import DATA_TYPES, FIELD_TYPES


class ActionForm(StarletteForm):
  topic = StringField(
    'Topic', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': input_class },
  )


class RoleForm(StarletteForm):
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )  
  current_action = QuerySelectField(
    'Current Action',
    collection = 'action', 
    projection = { 'topic': 1 }, 
    display_member = lambda data: f'{data["topic"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class },
  )
  action_date = DateField(
    'Action Date', 
    render_kw = { 'class': input_class, 'data-type': 'datetime' },
  )
  action_list = QuerySelectMultipleField(
    'Actions',
    collection = 'action', 
    projection = { 'topic': 1 }, 
    display_member = lambda data: f'{data["topic"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
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
    render_kw = { 'autofocus': 'true', 'class': input_class },
  )
  label_plural = StringField(
    'Plural Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  to_string = StringField(
    'To String',
    render_kw = { 'class': input_class },
  )
  order_by = QuerySelectMultipleField(
    'Order By',
    collection = 'model_field', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class },
  )
  page_size = IntegerField(
    'Page Size',
    render_kw = { 'class': input_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class ModelRecordTypeForm(StarletteForm):
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': input_class },
  )


class ModelFieldForm(StarletteForm):
  model_id = QuerySelectField(
    'Model',
    collection = 'model', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators=[DataRequired()],
    render_kw = { 'class': input_class },
  )
  # data_type = SelectField(
  #   'Data Type', 
  #   validators = [DataRequired()],
  #   choices = DATA_TYPES,
  #   render_kw = { 'class': select_class },
  # )
  data_type = QuerySelectField(
    'Data Type', 
    collection = 'data_type', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()],
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'class': select_class },
  )
  default_value = StringField(
    'Default Value',
    render_kw = { 'class': input_class },
  )
  default_value_use_quotes = ToggleSwitchField(
    'Default Value Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  # field_type = SelectField(
  #   'Field Type', 
  #   validators = [DataRequired()],
  #   choices = FIELD_TYPES,
  #   render_kw = { 'class': select_class },
  # )
  field_type = QuerySelectField(
    'Field Type', 
    collection = 'field_type', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()],
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'class': select_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class ModelFieldAttributeForm(StarletteForm):
  model_field_id = QuerySelectField(
    'Model Field', 
    collection = 'model_field', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
  )
  attribute_key = StringField(
    'Key', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  attribute_value = StringField(
    'Value', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  attribute_value_use_quotes = ToggleSwitchField(
    'Attribute Value Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  sequence = IntegerField(
    'Sequence', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class ModelFieldChoiceForm(StarletteForm):
  model_field_id = QuerySelectField(
    'Model Field', 
    collection = 'model_field', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  name_use_quotes = ToggleSwitchField(
    'Name Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  sequence = IntegerField(
    'Sequence', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class ModelFieldValidatorForm(StarletteForm):
  model_field_id = QuerySelectField(
    'Model Field', 
    collection = 'model_field', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  sequence = IntegerField(
    'Sequence', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class PageLayoutForm(StarletteForm):
  model_id = QuerySelectField(
    'Model', 
    collection = 'model', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
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
    render_kw = { 'autofocus': 'true', 'class': select_class },
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  element_list = FieldList(StringField(
    'Element',
  ))
  field_list = FieldList(FormField(
    ModelFieldForm
  ))
  related_list = FieldList(FormField(
    ModelForm
  ))
  role_list = FieldList(FormField(
    RoleForm
  ))
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class TabForm(StarletteForm):
  model_id = QuerySelectField(
    'Model', 
    collection = 'model', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  sequence = IntegerField(
    'Sequence', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class AppForm(StarletteForm):
  label = StringField(
    'Label', 
    validators=[DataRequired()],
    render_kw = { 'autofocus': 'true', 'class': input_class },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )
  description = StringField(
    'Description',
    render_kw = { 'class': input_class },
  )
  logo = StringField(
    'Logo',
    render_kw = { 'class': input_class },
  )
  tab_list = FieldList(FormField(
    TabForm
  ))
  role_list = FieldList(FormField(
    RoleForm
  ))
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )



