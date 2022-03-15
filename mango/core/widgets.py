# http://phdesign.com.au/programming/wtforms-selectfield-custom-option-attributes/
# https://gist.github.com/felipeblassioli/43a57eaa575679463d01
# https://wtforms.readthedocs.io/en/3.0.x/widgets/
# https://stackoverflow.com/questions/14510630/wtforms-creating-a-custom-widget
# https://stackoverflow.com/questions/16799388/create-a-custom-field-in-wtforms
# https://github.com/adamculpepper/toggle-radios
# https://www.cssscript.com/demo/segmented-control-toggle-radio/
# https://github.com/ViniChab/VC-Toggle-Switch
# https://www.cssscript.com/demo/ios-vc-toggle-switch/

from markupsafe import Markup
from wtforms.widgets.core import html_params


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

        html = ['<div class="toggle-switch-container" %s>' % html_params(**kwargs)]
        html.append(f'<label for="{field.id}" class="toggle-switch">')
        if field.data:
            html.append(f'<input type="checkbox" id="{field.id}" name="{field.id}" class="peer toggle-switch-input focus:border-none focus:shadow-none focus:rounded-none focus:ring-transparent" checked="checked">')
        else:
            html.append(f'<input type="checkbox" id="{field.id}" name="{field.id}" class="peer toggle-switch-input focus:border-none focus:shadow-none focus:rounded-none focus:ring-transparent">')
        html.append(f'<span data-on="Yes" data-off="No" class="toggle-switch-label peer-focus:border peer-focus:border-emerald-600"></span>')
        html.append('<span class="toggle-switch-handle"></span>')
        html.append('</label>')
        html.append('</div>')
        return Markup(''.join(html))
