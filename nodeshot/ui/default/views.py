from django.conf import settings
from django.shortcuts import render

from nodeshot.core.nodes.models import Node, Status
from nodeshot.core.layers.models import Layer


# TODO
# improve spaghetti code
def index(request):
    layers = Layer.objects.published()
    
    statuses = Status.objects.all()
    statuses_list = []
    
    for status in statuses:
        status.node_count = Node.objects.published().filter(
            layer__is_published=True, status_id=status.id
        ).select_related('layer').count()
        
        try:
            icon = status.statusicon_set.all()[0]
            status.background_color = icon.background_color
            status.foreground_color = icon.foreground_color
        except IndexError:
            pass
        
        statuses_list.append(status)
    
    context = {
        'layers': layers,
        'statuses': statuses_list
    }
    return render(request, 'index.html', context)
