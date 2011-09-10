from django import template
from django.template.defaultfilters import stringfilter
from nodeshot.utils import jslugify
register = template.Library()

@register.filter(name='jslugify')
@stringfilter
def jslugify_filter(value):
    """
    Template filter that executes jslugify()
    """
    return jslugify(value)