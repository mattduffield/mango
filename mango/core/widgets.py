# http://phdesign.com.au/programming/wtforms-selectfield-custom-option-attributes/
# https://gist.github.com/felipeblassioli/43a57eaa575679463d01
# https://wtforms.readthedocs.io/en/3.0.x/widgets/
# https://stackoverflow.com/questions/14510630/wtforms-creating-a-custom-widget
# https://stackoverflow.com/questions/16799388/create-a-custom-field-in-wtforms

from markupsafe import Markup
from wtforms.widgets.core import html_params


class TagsWidget:
    """
    Renders a select field allowing custom attributes for options.
    Expects the field to be an iterable object of Option fields.
    The render function accepts a dictionary of option ids ("{field_id}-{option_index}")
    which contain a dictionary of attributes to be passed to the option.

    Example:
    form.customselect(option_attr={"customselect-0": {"disabled": ""} })
    """

    def __init__(self, multiple=True):
        self.multiple = multiple

    def __call__(self, field, option_attr=None, **kwargs):
        if option_attr is None:
            option_attr = {}
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True

        html = ['<multi-select %s>' % html_params(name=field.name, **kwargs)]
        html.append(f'<input list="{field.id}_fields">')
        html.append(f'<datalist id="{field.id}_fields">')
        # html.append('''
        #   <option value="name">Name</option>
        #   <option value="name_plural">Name Plural</option>
        #   <option value="label" data-selected="true">Label</option>
        #   <option value="label_plural" data-selected="true">Label Plural</option>
        #   <option value="list_url" data-selected="true">List URL</option>
        # ''')
        for option in field:
            if field.data and option.data in field.data:
              attr = option_attr.get(option.id, {"data-selected": "true"})
            else:
              attr = option_attr.get(option.id, {})
            html.append(option(**attr))
        html.append('</datalist>')
        html.append('</multi-select>')
        return Markup(''.join(html))
