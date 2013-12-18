from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics, permissions, authentication
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from nodeshot.core.base.mixins import ListSerializerMixin
from nodeshot.core.base.utils import Hider
from nodeshot.core.nodes.views import NodeList
from nodeshot.core.nodes.serializers import NodeGeoSerializer
from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer
from .serializers import *


class ServiceList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list of Open 311 services.
    
    ### POST
    
    Create new service if authorized (admins and allowed users only).
    """
    model= Layer
    queryset = Layer.objects.published()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class= ServiceListSerializer
    #pagination_serializer_class = PaginatedLayerListSerializer
    #paginate_by_param = 'limit'
    #paginate_by = None

service_list = ServiceList.as_view()


class ServiceDefinition(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve details of specified serviceNode.
    
    """
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    model= Layer
    queryset = Layer.objects.published()
    serializer_class= ServiceDetailSerializer
    lookup_field = 'slug'

service_definition = ServiceDefinition.as_view()


class RequestList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve requests.
    
    ### POST
    
    Post a request
    """
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    #model= Node
    queryset = Node.objects.published()
    serializer_class= RequestListSerializer
    renderer_classes = (JSONRenderer,)
    
    def post(self, request, format=None):
        attributes = self.request.POST
        if not 'action' in attributes.keys():
            response="Please specify an action"
            return Response(response)
        else:
            #action=attributes.action
            return Response('ok')
        #nodes_count = Node.objects.count()
        #content = {'nodes': nodes_count}
        return Response(attributes)
    
    #def get_queryset(self):
    #    """
    #    Optionally restricts the returned nodes
    #    by filtering against a `search` query parameter in the URL.
    #    """
    #    # retrieve all nodes which are published and accessible to current user
    #    # and use joins to retrieve related fields
    #    queryset = super(RequestList, self).get_queryset().select_related('layer', 'status', 'user')
    #    
    #    # Control on attributes inserted
    #    attributes = self.request.QUERY_PARAMS
    #    
    #    #if search is not None:
    #    #    search_query = (
    #    #        Q(name__icontains=search) |
    #    #        Q(slug__icontains=search) |
    #    #        Q(description__icontains=search) |
    #    #        Q(address__icontains=search)
    #    #    )
    #    #    # add instructions for search to queryset
    #    #    queryset = queryset.filter(search_query)
    #    
    #    #return queryset
    #    return Response('no')
    
request_list = RequestList.as_view()

    
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


