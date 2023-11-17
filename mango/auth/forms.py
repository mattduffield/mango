import os
import markupsafe
from typing import Text
from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
from wtforms import (
  StringField, 
  TextAreaField, 
  PasswordField, 
  EmailField, 
  SelectField,
  BooleanField,
  FormField,
  Form,
)
from wtforms.validators	import DataRequired, Email, EqualTo, NoneOf, ValidationError
from mango.db.rest import find_one_sync
from mango.db.models import QueryOne
from mango.core.constants import input_class

DATABASE_NAME = os.environ.get('DATABASE_NAME')

def does_collection_field_exist(collection:str, field_name:str, field_value:str, database:str = DATABASE_NAME):
  payload = {
    'database': database,
    'collection': collection, 
    'query_type': 'find_one',
    'query': {
      field_name: field_value
    }, 
  }
  query = QueryOne.parse_obj(payload)
  found = find_one_sync(query)
  return found

def does_email_exist(email:str, database:str = DATABASE_NAME):
  payload = {
    'database': database,
    'collection': 'user', 
    'query_type': 'find_one',
    'query': {
      'email': email
    }, 
  }
  query = QueryOne.parse_obj(payload)
  found = find_one_sync(query)
  return found

def unique_username_validator(form, field):
    """ Username must be unique. This validator may NOT be customized."""
    if does_collection_field_exist(collection='user', field_name='username', field_value=field.data):
        raise ValidationError('This Username is already in use. Please try another one.')

def unique_email_validator(form, field):
    """ Email must be unique. This validator may NOT be customized."""
    if does_email_exist(field.data):
        raise ValidationError('This Email is already in use. Please try another one.')

class LoginForm(StarletteForm):
  email = StringField('Email', validators=[DataRequired()], render_kw={"autofocus": "true"})
  password = StringField('Password', validators=[DataRequired()])


class SignupForm(StarletteForm):
  first_name = StringField(
    'First Name', 
    validators=[
      DataRequired('First Name is required.')
    ], 
    render_kw={"autofocus": "true", "class": input_class},
    description='Required. 25 characters or fewer.',
  )
  last_name = StringField(
    'Last Name', 
    validators=[
      DataRequired('Last Name is required.')
    ], 
    render_kw={"class": input_class},
    description='Required. 25 characters or fewer.',
  )
  username = StringField(
    'Username', 
    validators=[
      DataRequired('Username is required.'),
      unique_username_validator,
    ], 
    render_kw={"class": input_class},
    description='Required. 25 characters or fewer.',
  )
  email = StringField(
    'Email', 
    validators=[
      DataRequired('Email is required.'),
      Email('Invalid email.'),
      unique_email_validator,
    ], 
    render_kw={"class": input_class},
    description='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
  )
  password = PasswordField(
    'Password', 
    validators=[DataRequired()],
    render_kw={"class": input_class},
    # description=markupsafe.Markup(f'Your password can’t be too similar to your other personal information.<br>Your password must contain at least 8 characters.<br>Your password can’t be a commonly used password.<br>Your password can’t be entirely numeric.'),
    description=markupsafe.Markup(f'Required.'),
  )
  password_confirmation = PasswordField(
    'Password confirmation', 
    validators=[DataRequired(), EqualTo('password', message='The two password fields did not match.')],
    render_kw={"class": input_class},
    description='Enter the same password as before, for verification.',
  )

class PasswordResetForm(StarletteForm):
  email = StringField(
    'Email', 
    validators=[DataRequired()], 
    render_kw={"autofocus": "true", "class": input_class}
  )
