from django.http import HttpResponse
from django.contrib.auth.models import User, Permission

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from .models import Node
from .serializers import *

from vectorformats.Formats import Django, GeoJSON
import simplejson as json


class NodeList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a list of nodes
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeListSerializer
    queryset = Node.objects.published().select_related('user', 'layer')

list = NodeList.as_view()
    
    
class NodeDetail(generics.RetrieveUpdateAPIView):
    """
    ### GET
    
    Retrieve details of specified node
    
    ### PUT & PATCH
    
    Edit node
    """
    lookup_field = 'slug'
    model = Node
    serializer_class= NodeDetailSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Node.objects.published().select_related('user', 'layer')

details = NodeDetail.as_view()


class NodeGeojsonList(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve nodes in GeoJSON format.
    """
    model = Node
    
    def get(self, request, *args, **kwargs):
        node = Node.objects.published()
        dj = Django.Django(geodjango="coords", properties=['name', 'description'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(node))  
        
        return Response(json.loads(string))

geojson_list = NodeGeojsonList.as_view()
