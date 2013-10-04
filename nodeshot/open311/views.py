from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics, permissions, authentication
from rest_framework.response import Response

from nodeshot.core.base.mixins import ListSerializerMixin
from nodeshot.core.base.utils import Hider
from nodeshot.core.nodes.views import NodeList
from nodeshot.core.nodes.serializers import NodeGeoSerializer

from nodeshot.core.layers.models import Layer
from .serializers import *

REVERSION_ENABLED = settings.NODESHOT['SETTINGS'].get('REVERSION_NODES', True)

if REVERSION_ENABLED:
    from nodeshot.core.base.mixins import RevisionCreate, RevisionUpdate
    
    class LayerListBase(RevisionCreate, generics.ListCreateAPIView):
        pass
    
    class LayerDetailBase(RevisionUpdate, generics.RetrieveUpdateAPIView):
        pass
else:
    class LayerListBase(generics.ListCreateAPIView):
        pass
    
    class LayerDetailBase(generics.RetrieveUpdateAPIView):
        pass


class ServiceList(LayerListBase):
    """
    ### GET
    
    Retrieve list of Open 311 services.
    
    ### POST
    
    Create new layer if authorized (admins and allowed users only).
    """
    model= Layer
    queryset = Layer.objects.published()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class= ServiceListSerializer
    pagination_serializer_class = PaginatedLayerListSerializer
    paginate_by_param = 'limit'
    paginate_by = None

service_list = ServiceList.as_view()


class ServiceDetail(LayerDetailBase):
    """
    ### GET
    
    Retrieve details of specified layer.
    
    ### PUT & PATCH
    
    Edit specified layer
    """
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    model= Layer
    queryset = Layer.objects.published()
    serializer_class= ServiceDetailSerializer
    lookup_field = 'slug'

service_detail = ServiceDetail.as_view()

    
#class LayerNodesList(ListSerializerMixin, NodeList):
#    """
#    ### GET
#    
#    Retrieve list of nodes of the specified layer
#    
#    Parameters:
#    
#     * `search=<word>`: search <word> in name of nodes of specified layer
#     * `limit=<n>`: specify number of items per page (defaults to 40)
#     * `limit=0`: turns off pagination
#    """
#    
#    layer = None
#    
#    def get_layer(self):
#        """ retrieve layer from DB """
#        if self.layer:
#            return
#        try:
#            self.layer = Layer.objects.get(slug=self.kwargs['slug'])
#        except Layer.DoesNotExist:
#            raise Http404(_('Layer not found'))
#    
#    def get_queryset(self):
#        self.get_layer()
#        return super(LayerNodesList, self).get_queryset().filter(layer_id=self.layer.id)
#    
#    def get_nodes(self, request, *args, **kwargs):
#        """ this method might be overridden by other modules (eg: interoperability) """
#        # ListSerializerMixin.list returns a serializer object
#        return (self.list(request, *args, **kwargs)).data
#    
#    def get(self, request, *args, **kwargs):
#        """ custom data structure """
#        self.get_layer()
#        content = LayerNodeListSerializer(self.layer, context=self.get_serializer_context()).data
#        content['nodes'] = self.get_nodes(request, *args, **kwargs)
#        return Response(content)
#    
#    post = Hider()
#
#nodes_list = LayerNodesList.as_view()


