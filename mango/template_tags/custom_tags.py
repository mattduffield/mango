'''
  Reference:
    https://github.com/dldevinc/jinja2-simple-tags
    https://michaelabrahamsen.com/posts/jinja2-custom-template-tags/
'''
from jinja2_simple_tags import StandaloneTag
# from settings import templates # We need this since we are rendering dynamic content...

class RenderColTag(StandaloneTag):
  tags = {'RenderCol'}

  def render(self, col, instance):
    # Usage:
    #   {% RenderCol col=col, instance=object %}
    result = ''
    name = col.get('name')
    html = col.get('html')
    if name and instance:
      result = instance.get(name, '')
      format = col.get('format')
      if format:
        fmt = getattr(result, format)
        if fmt:
          result = fmt()
      if callable(result):
        result = result()
    if html and instance:
      context = {'object': instance}
      template = templates.env.from_string(html)
      result = template.render(context)
    return result

def register_tags(templates):
  templates.env.add_extension(RenderColTag)  

# templates.env.add_extension(RenderColTag)
