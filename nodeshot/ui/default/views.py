from django.conf import settings
from django.shortcuts import render

from nodeshot.core.nodes.models import Node, Status
from nodeshot.core.layers.models import Layer


# TODO
# improve spaghetti code
def index(request):
    layers = Layer.objects.published()
    
    context = {
        'layers': layers
    }
    return render(request, 'index.html', context)
