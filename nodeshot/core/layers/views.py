import simplejson as json
from vectorformats.Formats import Django, GeoJSON

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from nodeshot.core.base.mixins import ListSerializerMixin
from nodeshot.core.base.utils import Hider
from nodeshot.core.nodes.views import NodeList

from .models import Layer
from .serializers import *


class LayerList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list of layers.
    
    ### POST
    
    Create new layer if authorized (admins and allowed users only).
    """
    model= Layer
    serializer_class= LayerListSerializer
    queryset = Layer.objects.published()
    pagination_serializer_class = PaginationSerializer
    paginate_by_param = 'limit'
    paginate_by = None
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

layer_list = LayerList.as_view()


class LayerDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve details of specified layer.
    """
    model= Layer
    serializer_class= LayerDetailSerializer
    queryset = Layer.objects.published()
    lookup_field = 'slug'

layer_detail = LayerDetail.as_view()

    
class LayerNodesList(ListSerializerMixin, NodeList):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer
    
    Parameters:
    
     * `search=<word>`: search <word> in name of nodes of specified layer
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    """
    
    layer = None
    
    def get_layer(self):
        """ retrieve layer from DB """
        if self.layer:
            return
        try:
            self.layer = Layer.objects.get(slug=self.kwargs['slug'])
        except Layer.DoesNotExist:
            raise Http404(_('Layer not found'))
    
    def get_queryset(self):
        self.get_layer()
        return super(LayerNodesList, self).get_queryset().filter(layer_id=self.layer.id)
    
    def get(self, request, *args, **kwargs):
        """ custom structure """
        self.get_layer()
        
        # here I had to mix the code of the interoperability module
        # not 100% satisfied but I couldn't find a better way
        if 'nodeshot.interoperability' in settings.INSTALLED_APPS and self.layer.is_external and hasattr(self.layer.external, 'get_nodes'):
            nodes = self.layer.external.get_nodes()
        else:
            # ListSerializerMixin.list returns a serializer object
            nodes = (self.list(request, *args, **kwargs)).data
        
        content = LayerNodeListSerializer(self.layer, context=self.get_serializer_context()).data
        content['nodes'] = nodes
        
        return Response(content)
    
    post = Hider()

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
        
        nodes = layer.node_set.published().accessible_to(request.user)
        dj = Django.Django(geodjango="coords", properties=['slug', 'name', 'address', 'description'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(nodes))  
        
        return Response(json.loads(string))

nodes_geojson_list = LayerAllNodesGeojsonList.as_view()