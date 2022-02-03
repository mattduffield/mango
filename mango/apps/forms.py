import markupsafe
from typing import Text
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
from wtforms.widgets import Select
from mango.core.forms import (
  label_class, 
  chk_class, 
  input_class, 
  select_class, 
  textarea_class, 
  multi_select_class,
  toggle_radio_class,
  toggle_switch_class,
  FieldForm,
  QuerySelectField,
  TagListField,
  TagsField,
  ToggleRadioField,
  ToggleSwitchField,
)
from mango.core.widgets import TagsWidget, ToggleRadioWidget


class FieldForm(Form):
  name: StringField('Name')
  label: StringField('Label')
  data_type: StringField('Data Type')
  default_value: StringField('Default Value')
  default_value_use_quotes: BooleanField('Default Value Use Quotes')
  element_type: StringField('Element Type')
  # element_html: StringField('Element HTML')
  # choices: List[Dict[str, str]] = []
  # validators: List[str] = []
  # element_attributes: dict = {}
  # fields: Optional[List['Field']]
  is_active: BooleanField('Is Active')


class FuncsForm(Form):
  str_func = StringField(
    'String Function',
  )
  object_display = StringField(
    'Object Display',
  )


class MetaDataForm(Form):
  search_index_name = StringField(
    'Search Index Name',
  )
  search_fields = TagsField(
    'Search Fields',
    separator=',',
    choices=[
      ('name', 'Name'),
      ('name_plural', 'Name Plural'),
      ('label', 'Label'),
      ('label_plural', 'Label Plural'),
      ('list_url', 'List URL'),
    ],
  )
  order_by = TagsField(
    'Order By',
    separator=',',
    choices=[
      ('name', 'Name'),
      ('name_plural', 'Name Plural'),    
      ('label', 'Label'),
      ('label_plural', 'Label Plural'),
      ('list_url', 'List URL'),
    ],
  )
  page_size = IntegerField(
    'Page Size',
  )


class AppForm(StarletteForm):
  name = StringField(
    'Name', 
    validators=[DataRequired()], 
    render_kw={  "autofocus":"true",  }
  )
  name_plural = StringField(
    'Plural Name', 
    validators=[DataRequired()] 
  )
  label = StringField(
    'Label', 
    validators=[DataRequired()] 
  )
  label_plural = StringField(
    'Plural Label', 
    validators=[DataRequired()] 
  )
  list_url = StringField(
    'List URL', 
    validators=[DataRequired()] 
  )
  list_route_name = StringField(
    'List Route Name', 
    validators=[DataRequired()] 
  )
  fields = FieldList(FormField(FieldForm))
  funcs = FormField(FuncsForm)
  meta_data = FormField(MetaDataForm)
  stage = ToggleRadioField(
    'Stage', 
    choices=[
      ('open', 'Open'),
      ('in_progress', 'In Progress'),
      ('closed', 'Closed'),
    ],
  )
  is_active = ToggleSwitchField(
    'Is Active?', 
  )
  has_policy = ToggleSwitchField(
    'Has Policy?', 
  )

  def layout_fields(self):
    fields = [
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'field': self.name, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.name_plural, 
            'css_class': input_class,
            'label_class': label_class
          },
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'field': self.label, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.label_plural, 
            'css_class': input_class,
            'label_class': label_class
          },          
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'field': self.list_url, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.list_route_name, 
            'css_class': input_class,
            'label_class': label_class
          },
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-col flex-1', 
        'fields': [
          {
            'type': 'row', 
            'content': 'Funcs',
            'css_class': 'text-lg mb-2',
          },
          {
            'type': 'row', 
            'css_class': 'flex flex-1 gap-4',
            'fields': [
              {
                'field': self.funcs.form.str_func, 
                'css_class': input_class,
                'label_class': label_class
              },
              {
                'field': self.funcs.form.object_display, 
                'css_class': input_class,
                'label_class': label_class
              },
            ],
          },
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-col flex-1', 
        'fields': [
          {
            'type': 'row', 
            'content': 'MetaData',
            'css_class': 'text-lg mb-2',
          },
          {
            'type': 'row', 
            'css_class': 'flex flex-1 gap-4',
            'fields': [
              {
                'field': self.meta_data.form.search_index_name, 
                'css_class': input_class,
                'label_class': label_class
              },
              {
                'field': self.meta_data.form.search_fields, 
                'css_class': multi_select_class,
                'label_class': label_class
              },
            ],
          },
          {
            'type': 'row', 
            'css_class': 'flex flex-1 gap-4',
            'fields': [
              {
                'field': self.meta_data.form.order_by, 
                'css_class': multi_select_class,
                'label_class': label_class
              },
              {
                'field': self.meta_data.form.page_size, 
                'css_class': input_class,
                'label_class': label_class
              },
            ],
          },
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'field': self.stage, 
            'css_class': toggle_radio_class,
            'label_class': label_class
          },
          {
            'field': self.is_active, 
            'css_class': toggle_switch_class,
            'label_class': label_class
          },
          {
            'field': self.has_policy, 
            'css_class': toggle_switch_class,
            'label_class': label_class
          },
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'macro': markupsafe.Markup('''crispy_table'''),
            'label_class': label_class
          },
        ]
      },
    ]
    return fields