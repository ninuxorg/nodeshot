from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from .models import Layer
from .serializers import *

from vectorformats.Formats import Django, GeoJSON
import simplejson as json

class LayerList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list of layers.
    """
    model= Layer
    serializer_class= LayerListSerializer
    queryset = Layer.objects.published()

list = LayerList.as_view()


class LayerDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve details of specified layer.
    """
    model= Layer
    serializer_class= LayerDetailSerializer
    queryset = Layer.objects.published()
    lookup_field = 'slug'

details = LayerDetail.as_view()

    
class LayerNodesList(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer
    """
    model = Layer
    serializer_class = LayerNodeListSerializer
    queryset = Layer.objects.published()
    lookup_field = 'slug'

nodes_list = LayerNodesList.as_view()


class LayerAllNodesGeojsonList(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer in GeoJSON format.
    """
    
    model = Layer
    
    def get(self, request, *args, **kwargs):
        """
        Get nodes of specified existing and published layer
        or otherwise return 404
        Outputs nodes in geojson format
        TODO: improve readability and cleanup

        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            layer = Layer.objects.get(slug=slug_value)
        except Exception:
            raise Http404(_('Layer not found'))
        node = layer.node_set.all()
        dj = Django.Django(geodjango="coords", properties=['name', 'description'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(node))  
        
        return Response(json.loads(string))

nodes_geojson_list = LayerAllNodesGeojsonList.as_view()

