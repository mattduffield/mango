from wtforms.validators import DataRequired, Optional


class DataRequiredIf(DataRequired):
  """Validator which makes a field required if another field is set and has a truthy value.

  Sources:
    - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
    - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

  """
  field_flags = ('requiredif',)

  def __init__(self, other_field_name, message=None, *args, **kwargs):
    self.other_field_name = other_field_name
    self.message = message

  def __call__(self, form, field):
    other_field = form[self.other_field_name]
    if other_field is None:
      raise Exception('no field named "%s" in form' % self.other_field_name)
    if bool(other_field.data):
      super(DataRequiredIf, self).__call__(form, field)


class OptionalIfFieldEqualTo(Optional):
  # a validator which makes a field optional if
  # another field has a desired value

  def __init__(self, other_field_name, value, *args, **kwargs):
    self.other_field_name = other_field_name
    self.value = value
    super(OptionalIfFieldEqualTo, self).__init__(*args, **kwargs)

  def __call__(self, form, field):
    other_field = form._fields.get(self.other_field_name)
    if other_field is None:
      raise Exception('no field named "%s" in form' % self.other_field_name)
    if other_field.data == self.value:
      super(OptionalIfFieldEqualTo, self).__call__(form, field)