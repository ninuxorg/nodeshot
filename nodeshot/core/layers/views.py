from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics, permissions, authentication
from rest_framework.response import Response

from nodeshot.core.base.mixins import ListSerializerMixin
from nodeshot.core.base.utils import Hider
from nodeshot.core.nodes.views import NodeList
from nodeshot.core.nodes.serializers import NodeGeoSerializer

from .models import Layer
from .serializers import *

HSTORE_ENABLED = settings.NODESHOT['SETTINGS'].get('HSTORE', True)


class LayerList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list of layers.
    
    ### POST
    
    Create new layer if authorized (admins and allowed users only).
    """
    model= Layer
    queryset = Layer.objects.published()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class= LayerListSerializer
    pagination_serializer_class = PaginatedLayerListSerializer
    paginate_by_param = 'limit'
    paginate_by = None

layer_list = LayerList.as_view()


class LayerDetail(generics.RetrieveUpdateAPIView):
    """
    ### GET
    
    Retrieve details of specified layer.
    """
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    model= Layer
    queryset = Layer.objects.published()
    serializer_class= LayerDetailSerializer
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


class LayerNodesGeoJSONList(LayerNodesList):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer in GeoJSON format.
    
    Parameters:
    
     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    """
    
    serializer_class = NodeGeoSerializer

nodes_geojson_list = LayerNodesGeoJSONList.as_view()


class LayerGeoJSONList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve layers in GeoJSON format.
    """
    
    serializer_class = GeoLayerListSerializer
    queryset = Layer.objects.published().exclude(area__isnull=True)

layers_geojson_list = LayerGeoJSONList.as_view()
