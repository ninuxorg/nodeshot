from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics, permissions, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer

from .base import SERVICES
from .serializers import *


class ServiceList(generics.ListAPIView):
    """
    Retrieve list of Open 311 services.
    """
    #model = Layer
    #queryset = Layer.objects.published()
    #permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class = ServiceListSerializer
    
    def get(self, request, *args, **kwargs):
        """ return several services for each layer """
        # init django rest framework specific stuff
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        
        # init empty list
        services = []
        
        # loop over each service
        for service_type in SERVICES.keys():
            # initialize serializers for layer
            services.append(
                serializer_class(
                    context=context,
                    service_type=service_type
                ).data
            )
        
        return Response(services)

service_list = ServiceList.as_view()


class ServiceDefinition(APIView):
    """
    Retrieve details of specified serviceNode.
    """
    
    def get(self, request, *args, **kwargs):
        service_type = kwargs['service_type']
        
        if service_type not in SERVICES.keys():
            return Response({ 'detail': _('Not found') }, status=404)
        
        serializers = {
            'node': ServiceNodeSerializer,
            'vote': ServiceNodeSerializer,
            'comment': ServiceNodeSerializer,
            'rating': ServiceNodeSerializer,
        }
        
        # init right serializer
        data = serializers[service_type]().data
        
        return Response(data)
    
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


