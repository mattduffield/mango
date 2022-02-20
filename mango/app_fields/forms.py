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
  #QuerySelectField,
  TagListField,
  TagsField,
  ToggleRadioField,
  ToggleSwitchField,
)
from mango.core.widgets import TagsWidget, ToggleRadioWidget


class KeyValueForm(Form):
  key = StringField('Key')
  value = StringField('Value')


class ChoicesForm(Form):
  name = StringField('Name')
  label = StringField('Label')


class AppFieldForm(StarletteForm):
  app_id = SelectField('App', 
    validators=[DataRequired()], 
    render_kw={ "autofocus":"true", }
  )
  # app_id = QuerySelectField('App', 
  #   collection='apps', 
  #   blank_text='Pick...', 
  #   projection={'label': 1}, 
  #   display_member=lambda data: f'{data["label"]}', 
  #   value_member=lambda data: f'{data["_id"]}',
  #   validators=[DataRequired()], 
  #   render_kw={ "autofocus":"true", }
  # )
  name = StringField('Name')
  label = StringField('Label')
  data_type = StringField('Data Type')
  default_value = StringField('Default Value')
  default_value_use_quotes = BooleanField('Default Value Use Quotes')
  element_type = StringField('Element Type')
  element_attributes = FieldList(FormField(KeyValueForm))
  choices = FieldList(FormField(ChoicesForm))
  validators = FieldList(StringField('Validator'))
  is_active = BooleanField('Is Active')

  def layout_fields(self):
    fields = [
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'field': self.app_id, 
            'css_class': select_class,
            'label_class': label_class
          },
          {
            'field': self.name, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.label, 
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
            'field': self.data_type, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.element_type, 
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
            'field': self.default_value, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.default_value_use_quotes, 
            'css_class': chk_class,
            'label_class': label_class
          },
        ]
      },
      {
        'type': 'row', 
        'css_class': 'flex flex-1 gap-4', 
        'fields': [
          {
            'field': self.validators, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.choices, 
            'css_class': input_class,
            'label_class': label_class
          },
          {
            'field': self.is_active, 
            'css_class': chk_class,
            'label_class': label_class
          },
        ]
      },
    ]
    return fields
