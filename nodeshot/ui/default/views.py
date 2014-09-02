import simplejson as json

from django.conf import settings
from django.shortcuts import render

from nodeshot.core.nodes.models import Node, Status
from nodeshot.core.layers.models import Layer

from .settings import settings, TILESERVER_URL, MAP_CENTER, MAP_ZOOM

if 'nodeshot.core.websockets' in settings.INSTALLED_APPS:
    from nodeshot.core.websockets import DOMAIN, PATH, PORT

    WEBSOCKETS = {
        'DOMAIN': DOMAIN,
        'PATH': PATH,
        'PORT': PORT
    }
else:
    WEBSOCKETS = False


# TODO
# improve spaghetti code
def index(request):
    layers = Layer.objects.published()
    layers_allowing_new_nodes = layers.filter(new_nodes_allowed=True)

    context = {
        'layers': layers,
        'layers_allowing_new_nodes': layers_allowing_new_nodes,
        'WEBSOCKETS': WEBSOCKETS,
        'TILESERVER_URL': TILESERVER_URL,
        'MAP_CENTER': MAP_CENTER,
        'MAP_ZOOM': MAP_ZOOM
    }
    return render(request, 'index.html', context)
