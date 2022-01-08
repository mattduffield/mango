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
