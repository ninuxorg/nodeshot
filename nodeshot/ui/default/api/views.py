from rest_framework.decorators import api_view
from rest_framework.response import Response
from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.models import Status
from nodeshot.core.layers.models import Layer
from nodeshot.core.cms.models import MenuItem
from nodeshot.core.nodes.serializers import NodeGeoSerializer, StatusListSerializer
from nodeshot.core.layers.serializers import LayerDetailSerializer
from nodeshot.core.cms.serializers import MenuSerializer


@api_view(('GET',))
def essential_data(request, format=None):
    """
    Retrieve nodes (geojson), status, layers and menu in one request.
    """
    nodes = Node.objects.published().accessible_to(request.user)
    layers = Layer.objects.published()
    status = Status.objects.all()
    menu = MenuItem.objects.published().filter(parent=None).accessible_to(request.user)
    context = { 'request': request }
    return Response({
        'nodes': NodeGeoSerializer(nodes, many=True, context=context).data,
        'layers': LayerDetailSerializer(layers, many=True, context=context).data,
        'status': StatusListSerializer(status, many=True, context=context).data,
        'menu': MenuSerializer(menu, many=True, context=context).data
    })
