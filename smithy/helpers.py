from django.template import Template, Context

def render_with_context(template, context):
    template = Template(template)
    context = Context(context)
    return template.render(context)
