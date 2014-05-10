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


# TODO
# improve spaghetti code
def index(request):
    layers = Layer.objects.published()
    
    context = {
        'layers': layers,
        'WEBSOCKETS': WEBSOCKETS,
        'TILESERVER_URL': settings.NODESHOT['SETTINGS'].get('TILESERVER_URL', '//a.tiles.mapbox.com/v3/nodeshot-cineca.i6kgg4hb/{z}/{x}/{y}.png')
    }
    return render(request, 'index.html', context)
