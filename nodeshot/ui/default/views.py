import simplejson as json

from django.conf import settings
from django.shortcuts import render

from nodeshot.core.nodes.models import Node, Status
from nodeshot.core.layers.models import Layer

if 'nodeshot.core.websockets' in settings.INSTALLED_APPS:
    from nodeshot.core.websockets import DOMAIN, PATH, PORT

    WEBSOCKETS = {
        'DOMAIN': DOMAIN,
        'PATH': PATH,
        'PORT': PORT
    }
else:
    WEBSOCKETS = False

TILESERVER_URL = settings.NODESHOT['SETTINGS'].get('TILESERVER_URL', '//a.tiles.mapbox.com/v3/nodeshot-cineca.i6kgg4hb/{z}/{x}/{y}.png')
MAP_CENTER = json.dumps(settings.NODESHOT['SETTINGS'].get('ADMIN_MAP_COORDS'))
MAP_ZOOM = settings.NODESHOT['SETTINGS'].get('FRONTEND_MAP_ZOOM', 4)


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
