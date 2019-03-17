from django.template import Template, Context
from requests_toolbelt.utils import dump

def render_with_context(template, context):
    template = Template(template)
    context = Context(context)
    return template.render(context)

def parse_dump_result(fun, obj):
    prefixes = dump.PrefixSettings('', '')
    try:
        result = bytearray()
        fun(obj, prefixes, result)
        return result.decode('utf-8')
    except Exception:
        return "Could not parse request as a string"
