# http://phdesign.com.au/programming/wtforms-selectfield-custom-option-attributes/
# https://gist.github.com/felipeblassioli/43a57eaa575679463d01
# https://wtforms.readthedocs.io/en/3.0.x/widgets/
# https://stackoverflow.com/questions/14510630/wtforms-creating-a-custom-widget
# https://stackoverflow.com/questions/16799388/create-a-custom-field-in-wtforms
# https://github.com/adamculpepper/toggle-radios
# https://www.cssscript.com/demo/segmented-control-toggle-radio/
# https://github.com/ViniChab/VC-Toggle-Switch
# https://www.cssscript.com/demo/ios-vc-toggle-switch/

import json
from markupsafe import Markup
from wtforms.widgets.core import html_params
from wtforms.widgets import TextInput, TextArea
from wtforms import widgets

class MangoInput:
  """
  Render a basic ``<input>`` field.

  This is used as the basis for most of the other input fields.

  By default, the `_value()` method will be called upon the associated field
  to provide the ``value=`` HTML attribute.
  """

  html_params = staticmethod(html_params)
  validation_attrs = ["required"]

  def __init__(self, input_type=None):
    if input_type is not None:
      self.input_type = input_type

  def __call__(self, field, **kwargs):
    kwargs.setdefault("id", field.id)
    kwargs.setdefault("type", self.input_type)
    if "value" not in kwargs:
      kwargs["value"] = field._value()
    flags = getattr(field, "flags", {})
    for k in dir(flags):
      if k in self.validation_attrs and k not in kwargs:
        kwargs[k] = getattr(flags, k)

    html = ['<div class="mt-1 relative rounded-md shadow-sm">']
    html.append(f'<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">')
    html.append('<span class="text-gray-500 sm:text-sm"> $ </span>')
    html.append('</div>')
    html.append(f'<input %s>')
    html.append('</div>')
    return Markup(''.join(html) % self.html_params(name=field.name, **kwargs))



class CurrencyWidget:
  def __init__(self):
    pass

  def __call__(self, field, option_attr=None, **kwargs):
    if option_attr is None:
      option_attr = {}
    if "required" not in kwargs and "required" in getattr(field, "flags", []):
      kwargs["required"] = True

    html = ['<div class="mt-1 relative rounded-md shadow-sm" %s>']
    html.append(f'<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">')
    html.append('<span class="text-gray-500 sm:text-sm"> $ </span>')
    html.append('</div>')

    if field.data:
      html.append(f'<input type="text" id="{field.id}" name="{field.id}" value="{field.data}" {html_params(**kwargs)}>')
    else:
      html.append(f'<input type="text" id="{field.id}" name="{field.id}" {html_params(**kwargs)}>')
    html.append('</div>')
    return Markup(''.join(html))

class CurrencyDecimalWidget(MangoInput):
  input_type = "number"
  validation_attrs = ["required", "max", "min", "step"]

  def __init__(self, step=None, min=None, max=None):
    self.step = step
    self.min = min
    self.max = max

  def __call__(self, field, **kwargs):
    if self.step is not None:
        kwargs.setdefault("step", self.step)
    if self.min is not None:
        kwargs.setdefault("min", self.min)
    if self.max is not None:
        kwargs.setdefault("max", self.max)
    return super().__call__(field, **kwargs)


class ToggleRadioWidget:
  def __init__(self):
    pass

  def __call__(self, field, option_attr=None, **kwargs):
    if option_attr is None:
      option_attr = {}
    kwargs.setdefault("id", field.id)
    if "required" not in kwargs and "required" in getattr(field, "flags", []):
      kwargs["required"] = True

    html = ['<div data-style="rounded" %s">' % html_params(name=field.name, **kwargs)]
    for option in field:
      if field.data and option.data in field.data:
        attr = option_attr.get(option.id, {"data-selected": "true"})
      else:
        attr = option_attr.get(option.id, {})
      html.append(option(**attr))
      html.append(f'<label for="{option.id}">{option.label.text}</label>')
    html.append('</div>')
    return Markup(''.join(html))


class ToggleSwitchWidget:
  def __init__(self):
    pass

  def __call__(self, field, option_attr=None, **kwargs):
    if option_attr is None:
      option_attr = {}
    if "required" not in kwargs and "required" in getattr(field, "flags", []):
      kwargs["required"] = True

    html = ['<span class="toggle-switch-container" %s>']
    html.append(f'<label for="{field.id}" class="toggle-switch">')
    if field.data:
      html.append(f'<input type="checkbox" id="{field.id}" name="{field.id}" class="peer toggle-switch-input focus:border-none focus:shadow-none focus:rounded-none focus:ring-transparent" checked="checked" {html_params(**kwargs)}>')
    else:
      html.append(f'<input type="checkbox" id="{field.id}" name="{field.id}" class="peer toggle-switch-input focus:border-none focus:shadow-none focus:rounded-none focus:ring-transparent" {html_params(**kwargs)}>')
    html.append(f'<span data-on="Yes" data-off="No" class="toggle-switch-label peer-focus:border peer-focus:border-emerald-600"></span>')
    html.append('<span class="toggle-switch-handle"></span>')
    html.append('</label>')
    html.append('</span>')
    return Markup(''.join(html))


class DatalistWidget(TextInput):
  """
  Custom widget to create an input with a datalist attribute
  """

  def __init__(self, datalist=[]):
    super(DatalistWidget, self).__init__()
    self.datalist = datalist

  def __call__(self, field, **kwargs):
    kwargs.setdefault('id', field.id)
    kwargs.setdefault('name', field.name)
    if "value" not in kwargs:
      kwargs["value"] = field._value()
    html = [u'<input type="text" list="{}_list" id="{}" name="{}" {}>'.format(field.id, field.id, field.name, html_params(**kwargs)),
            u'<datalist id="{}_list">'.format(field.id)]

    for item in field.datalist:
      html.append(u'<option value="{}">'.format(item))

    html.append(u'</datalist>')
    return Markup(u''.join(html))


class CodeMirrorWidget(TextArea):
  """CodeMirror Widget for CodeMirrorField
    Add CodeMirror JavaScript library paramaters to widget
    :param language: source code language
    :param config: CodeMirror field config
  """

  POST_HTML = '''
    <script>
      var editor_for_{0} = CodeMirror.fromTextArea(
        document.getElementById('codemirror-{0}'),
        {1}
      );
    </script>
  '''

  def __init__(self, config=None):
    super(CodeMirrorWidget, self).__init__()
    self.config = config or {}

  def __call__(self, field, **kwargs):
    field_id = 'codemirror-' + field.id
    html = super(CodeMirrorWidget, self).__call__(field, id=field_id, **kwargs)
    content = self._generate_content()
    content = content.replace('"function(cm) { cm.foldCode(cm.getCursor()); }"', 'function(cm) { cm.foldCode(cm.getCursor()); }')
    post_html = self.__class__.POST_HTML.format(field.id, content)
    return html + Markup(post_html)

  def _generate_content(self):
    """Dumps content using JSON to send to CodeMirror"""
    return json.dumps(self.config, separators=(',', ': '))


class FileUploadWidget:
  def __init__(self):
    pass

  def __call__(self, field, option_attr=None, **kwargs):
    if option_attr is None:
      option_attr = {}
    if "required" not in kwargs and "required" in getattr(field, "flags", []):
      kwargs["required"] = True

    html = f'''
      <div class="mt-1 sm:col-span-2 sm:mt-0">
        <div class="flex max-w-lg justify-center rounded-md border-2 border-dashed border-gray-300 px-6 pt-5 pb-6">
          <div class="space-y-1 text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <div class="flex text-sm text-gray-600">
              <label for="{field.id}" class="relative cursor-pointer rounded-md bg-white font-medium text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:text-indigo-500">
                <span>Upload a file</span>
                <input id="{field.id}" name="{field.id}" type="file" class="sr-only" {html_params(**kwargs)}>
              </label>
              <p class="pl-1">or drag and drop</p>
            </div>
            <p class="text-xs text-gray-500">PDF, PNG, JPG up to 10MB</p>
          </div>
        </div>
      </div>      
    '''

    return Markup(html.strip())


class TomSelectWidget(widgets.Select):
  """
    `TomSelect <https://tom-select.js.org/docs/>`_ styled select widget.
    You must include tom-select.complete.js,and tom-select stylesheet for it to
    work.
  """
  def __call__(self, field, **kwargs):
    kwargs.setdefault('data-role', u'tom-select')

    allow_blank = getattr(field, 'allow_blank', False)
    if allow_blank and not self.multiple:
      kwargs['data-allow-blank'] = u'1'

    return super(TomSelectWidget, self).__call__(field, **kwargs)
