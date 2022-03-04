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
  # StringField,
  SubmitField,
  HiddenField,
  PasswordField,
  TextAreaField,
  FormField,
  # FieldList,
  Form,
)
from wtforms.validators	import DataRequired, NoneOf
from mango.core.fields import QuerySelectField, QuerySelectMultipleField, ToggleSwitchField
from mango.core.fields import (
  StringField2 as StringField,
  FieldList2 as FieldList
)
from mango.core.constants import chk_class, input_class, label_class, select_class, select_multiple_class, textarea_class, toggle_radio_class, toggle_switch_class, hs_element_type, hs_config_tom_select, hs_field_type
from mango.core.choices import DATA_TYPES, FIELD_TYPES
from mango.core.validators import DataRequiredIf, OptionalIfFieldEqualTo


class KeyValueForm(Form):
  key = StringField(
    'Key',
    validators= [],
    render_kw = { 'class': input_class },
  )
  value = StringField(
    'Value',
    validators= [],
    render_kw = { 'class': input_class },
  )


class ActionForm(StarletteForm):
  topic = StringField(
    'Topic', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'on input toLowerUri(me)' },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': input_class },
  )


class RoleForm(StarletteForm):
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class },
  )  
  # current_action = QuerySelectField(
  #   'Current Action',
  #   collection = 'action', 
  #   projection = { 'topic': 1 }, 
  #   display_member = lambda data: f'{data["topic"]}', 
  #   value_member = lambda data: f'{data["_id"]}',
  #   render_kw = { 'class': select_class },
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
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
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
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
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
    query = { 'model_name': lambda data: data["name"] },
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
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
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
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
  model_name = QuerySelectField(
    'Model',
    collection = 'model', 
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    validators = [DataRequired()], 
    allow_blank = True,
    blank_text = 'Pick...',
    render_kw = { 'autofocus': 'true', 'class': select_class },
    wrapper_class = 'flex-1',
  )
  label = StringField(
    'Label', 
    validators = [DataRequired()], 
    render_kw = { 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
    wrapper_class = 'flex-1',
  )
  name = StringField(
    'Name', 
    validators=[DataRequired()],
    render_kw = { 'class': input_class },
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
    render_kw = { 'class': select_class },
    wrapper_class = 'flex-1',
  )
  is_optional = ToggleSwitchField(
    'Is Optional?', 
    render_kw = { 'class': chk_class },
    wrapper_class = '',
  )
  is_list = ToggleSwitchField(
    'Is List?', 
    render_kw = { 'class': chk_class },
    wrapper_class = '',
  )
  default_value = StringField(
    'Default Value',
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  default_value_use_quotes = ToggleSwitchField(
    'Default Value Use Quotes?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
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
    render_kw = { 'class': select_class, 'data-script': hs_field_type },
    wrapper_class = 'flex-1',
  )
  validator_list = FieldList(
    StringField(
      'Validator',
      render_kw = { 'class': input_class },
    ),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  attribute_list = FieldList(
    FormField(KeyValueForm),
    min_entries=1,
    wrapper_class = 'flex-1',
  )
  collection = StringField(
    'Collection',
    render_kw = { 'class': input_class },
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
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  value_member = StringField(
    'Value Member',
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  allow_blank = ToggleSwitchField(
    'Allow Blank?', 
    render_kw = { 'class': chk_class },
    wrapper_class = '',
  )
  blank_text = StringField(
    'Blank Text',
    render_kw = { 'class': input_class },
    wrapper_class = 'flex-1',
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
    wrapper_class = 'flex-1',
  )

  # def __init__(self, request: StarletteRequest, *args, **kwargs):
  #   self.allow_blank.wrapper_class = 'test-class'
  #   super().__init__(request=request, args=args, kwargs=kwargs)


class ModelFieldAttributeForm(StarletteForm):
  model_field_id = QuerySelectField(
    'Model Field', 
    collection = 'model_field', 
    projection = { 'label': 1, 'name': 1 }, 
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
    projection = { 'label': 1, 'name': 1 }, 
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
    render_kw = { 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
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
    projection = { 'label': 1, 'name': 1 }, 
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


class LayoutLevel4Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class LayoutLevel3Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  items = FieldList(
    FormField(LayoutLevel4Form)
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class LayoutLevel2Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  items = FieldList(
    FormField(LayoutLevel3Form)
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class LayoutLevel1Form(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  items = FieldList(
    FormField(LayoutLevel2Form)
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
  )


class LayoutForm(Form):
  element_type = StringField(
    'Element Type', 
    validators = [DataRequired()],
    render_kw = { 'class': input_class, 'data-script': hs_element_type },
  )
  field = StringField(
    'Field', 
    render_kw = { 'class': input_class },
  )
  css_class = StringField(
    'CSS Class', 
    render_kw = { 'class': input_class },
  )
  css_class_use_quotes = ToggleSwitchField(
    'CSS Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  inner_text = StringField(
    'InnerText', 
    render_kw = { 'class': input_class },
  )
  inner_html = StringField(
    'InnerHTML', 
    render_kw = { 'class': input_class },
  )
  label_class = StringField(
    'Label Class', 
    render_kw = { 'class': input_class },
  )
  label_class_use_quotes = ToggleSwitchField(
    'Label Class Use Quotes?', 
    render_kw = { 'class': chk_class },
  )
  items = FieldList(
    FormField(LayoutLevel1Form)
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
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
    render_kw = { 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired('label')],
    render_kw = { 'class': input_class },
  )
  element_list = FieldList(StringField(
    'Element',
  ))
  field_list = FieldList(FormField(
    ModelFieldForm
  ))
  # related_list = FieldList(FormField(
  #   ModelForm
  # ))
  related_list = QuerySelectMultipleField(
    'Related List',
    collection = 'model', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
  )
  # role_list = FieldList(FormField(
  #   RoleForm
  # ))
  role_list = QuerySelectMultipleField(
    'Roles',
    collection = 'role', 
    projection = { 'label': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["_id"]}',
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
  )
  # items = TextAreaField(
  #   'Items',
  #   render_kw = { 'class': textarea_class },
  # )
  items = FieldList(
    FormField(LayoutForm)
  )
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
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
    render_kw = { 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
  )
  name = StringField(
    'Name', 
    validators = [DataRequired('label')],
    render_kw = { 'class': input_class },
  )
  field_list = QuerySelectMultipleField(
    'Field List',
    collection = 'model_field', 
    query = { 'model_name': lambda data: data["model_name"] },
    projection = { 'label': 1, 'name': 1 }, 
    display_member = lambda data: f'{data["label"]}', 
    value_member = lambda data: f'{data["name"]}',
    render_kw = { 'class': select_class, 'data-script': hs_config_tom_select },
  )
  is_default = ToggleSwitchField(
    'Is Default?', 
    render_kw = { 'class': chk_class },
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
    render_kw = { 'class': chk_class },
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
    render_kw = { 'autofocus': 'true', 'class': input_class, 'data-script': 'on input copyToLowerSnake(me, "name")' },
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
