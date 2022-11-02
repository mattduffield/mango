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
      html.append(f'<input type="text" id="{field.id}" name="{field.id}" class="focus:ring-emerald-500 focus:border-emerald-500 block w-full pl-7 pr-12 text-gray-700 border-gray-300 rounded" value="{field.data}" {html_params(**kwargs)}>')
    else:
      html.append(f'<input type="text" id="{field.id}" name="{field.id}" class="focus:ring-emerald-500 focus:border-emerald-500 block w-full pl-7 pr-12 text-gray-700 border-gray-300 rounded" {html_params(**kwargs)}>')
    html.append('</div>')
    return Markup(''.join(html))


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
      //var txt = document.getElementById('codemirror-{0}');
      //console.log(txt);
      //if (txt.form) txt.form.addEventListener('submit', () => txt.value = editor_for_{0}.getValue())
      //editor_for_{0}.on('change', editor => editor.save());
      //editor_for_{0}.foldCode(CodeMirror.Pos(0, 0));
    </script>
  '''

  def __init__(self, config=None):
    super(CodeMirrorWidget, self).__init__()
    self.theme = 'monokai'
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
    # concat into a dict
    dic = self.config
    # dic['mode'] = self.language
    if self.theme:
        dic['theme'] = self.theme
    # dumps with json
    return json.dumps(dic, indent=2, separators=(',', ': '))


