from django import template
from leaflet.templatetags.leaflet_tags import leaflet_map


register = template.Library()


@register.inclusion_tag('leaflet/_load_map.html')
def nodeshot_map(name, callback=None, fitextent=True, creatediv=True, loadevent='load'):
    return leaflet_map(name, callback=None, fitextent=True, creatediv=True, loadevent='load')
