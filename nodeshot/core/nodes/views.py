from django.contrib.auth.models import User, Permission
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from .models import Node, Image
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

node_list = NodeList.as_view()
    
    
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

node_details = NodeDetail.as_view()


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


### ------ Images ------ ###


class NodeImageList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a list of image of the specified node.
    Node must exist and be published.
    
    ### POST
    
    Upload a new image, TODO!
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Image
    
    # TODO:
    # create a dedicated serializer
    # which puts added and updated as last attributes
    # removes node_id
    # inserts full url path to where image is located
    
    def get_queryset(self):
        """
        Get images of specified existing and published node
        or otherwise return 404
        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            node = Node.objects.get(slug=slug_value, is_published=True)
        except Exception:
            raise Http404(_('Node not found'))
        
        # TODO: implement access_level
        return node.image_set.all()
    

node_images = NodeImageList.as_view()