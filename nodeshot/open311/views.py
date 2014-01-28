from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics, permissions, authentication, status
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
            'vote': ServiceVoteSerializer,
            'comment': ServiceCommentSerializer,
            'rate': ServiceRatingSerializer,
        }
        
        # init right serializer
        data = serializers[service_type]().data
        
        return Response(data)
    
service_definition = ServiceDefinition.as_view()


class RequestInsert(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve requests.
    
    ### POST
    
    Post a request
    """
    authentication_classes = (authentication.SessionAuthentication,)
    #serializer_class= NodeRequestSerializer
    model=Node
    
    def get_custom_data(self):
        """ additional request.DATA """
        
        return {
            'user': self.request.user.id
        }
    
    def get(self, request, *args, **kwargs):
        service_code = request.GET['service_code']
        
        if service_code not in SERVICES.keys():
            return Response({ 'detail': _('Service not found') }, status=404)
        
        #serializers = {
        #    'node': ServiceNodeSerializer,
        #    'vote': ServiceVoteSerializer,
        #    'comment': ServiceCommentSerializer,
        #    'rate': ServiceRatingSerializer,
        #}
        #
        ## init right serializer
        #data = serializers[service_type]().data
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        service_code = request.POST['service_code']
        
        if service_code not in SERVICES.keys():
            return Response({ 'detail': _('Service not found') }, status=404)
        
        serializers = {
            'node': NodeRequestSerializer,
            'vote': VoteRequestSerializer,
            'comment': CommentRequestSerializer,
            'rate': RatingRequestSerializer,
        }
        
        # init right serializer
        kwargs['service_code'] = service_code
        kwargs['serializer'] = serializers[service_code]
        
        user=self.get_custom_data()
        
        request.UPDATED = request.POST.copy()
        request.UPDATED['user'] = user['user']
        
        if service_code == 'node':
            layer=Layer.objects.get(slug=request.POST['layer'])           
            request.UPDATED['layer'] = layer.id

        return self.create(request, *args, **kwargs)
   
    def create(self, request, *args, **kwargs):
        
        #service_request={'service_code':"node","name": "montesacro10","slug":"montesacro10","layer": 1,"lat": "22.5253","lng": "41.8890","description": "test","geometry": "POINT (22.5253334454477372 41.8890404543067518)"}
        serializer = kwargs['serializer']( data=request.UPDATED, files=request.FILES)
        
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            response_311=kwargs['service_code'] + '-' + str(self.object.id)
            return Response(response_311, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #def create(self, request, *args, **kwargs):
    #    serializer = self.get_serializer(data=request.DATA, files=request.FILES)
    #
    #    if serializer.is_valid():
    #        self.pre_save(serializer.object)
    #        self.object = serializer.save(force_insert=True)
    #        self.post_save(self.object, created=True)
    #        headers = self.get_success_headers(serializer.data)
    #        return Response(serializer.data, status=status.HTTP_201_CREATED,
    #                        headers=headers)
    #
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
service_request = RequestInsert.as_view()


