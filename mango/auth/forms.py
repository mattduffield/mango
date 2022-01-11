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
from wtforms.validators	import DataRequired, NoneOf
from mango.core.forms import (
  label_class, 
  chk_class, 
  input_class, 
  select_class, 
  textarea_class, 
  QuerySelectField
)


class LoginForm(StarletteForm):
  email = StringField('Email', validators=[DataRequired()], render_kw={"autofocus": "true"})
  password = StringField('Password', validators=[DataRequired()])


class SignupForm(StarletteForm):
  email = StringField(
    'Email', 
    validators=[DataRequired()], 
    render_kw={"autofocus": "true"},
    description='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
  )
  password = PasswordField(
    'Password', 
    validators=[DataRequired()],
    description=markupsafe.Markup(f'Your password can’t be too similar to your other personal information.<br>Your password must contain at least 8 characters.<br>Your password can’t be a commonly used password.<br>Your password can’t be entirely numeric.'),
  )
  password_confirmation = PasswordField(
    'Password confirmation', 
    validators=[DataRequired()],
    description='Enter the same password as before, for verification.',
  )
