from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from nodeshot.core.base.mixins import ACLMixin,CustomDataMixin

from .models import Node, Image
from .serializers import *

from vectorformats.Formats import Django, GeoJSON
import simplejson as json


def get_queryset_or_404(queryset, kwargs):
    """
    Checks if object returned by queryset exists
    """
    # ensure exists
    try:
        obj = queryset.get(**kwargs)
    except Exception:
        raise Http404(_('Not found'))
    
    return obj


class NodeList(ACLMixin, generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a list of nodes
    
    **Pagination**:
    
    Parameters:
    
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Node.objects.published()
    serializer_class = NodeListSerializer
    serializer_custom_class = NodeCreatorSerializer
    pagination_serializer_class = PaginatedNodeListSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
    def get_queryset(self):
        """
        Optionally restricts the returned nodes
        by filtering against a `search` query parameter in the URL.
        """
        # retrieve all nodes which are published and accessible to current user
        # and use joins to retrieve related fields
        queryset = super(NodeList, self).get_queryset()
        # retrieve value of querystring parameter "search"
        search = self.request.QUERY_PARAMS.get('search', None)
        
        if search is not None:
            # add instructions for search to queryset
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
node_list = NodeList.as_view()
    
    
class NodeDetail(ACLMixin, generics.RetrieveUpdateAPIView):
    """
    ### GET
    
    Retrieve details of specified node
    
    ### PUT & PATCH
    
    Edit node
    """
    lookup_field = 'slug'
    model = Node
    serializer_class = NodeDetailSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Node.objects.published().select_related('user', 'layer')

node_details = NodeDetail.as_view()


class NodeGeojsonList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve nodes in GeoJSON format.
    """
    #model = Node
    #paginate_by = 10
    paginate_by_param = 'results'
    serializer_class = GeojsonNodeListSerializer
    #pagination_serializer_class = NodePaginationSerializer
    
    #def get_queryset(self):
        #"""
        #TODO: improve readability and cleanup and make it work !!
        #"""
        ##node = Node.objects.published().accessible_to(request.user)
        ##super(NodeGeojsonList, self).initial(request, *args, **kwargs)
        #node = Node.objects.published()
        #dj = Django.Django(geodjango="coords", properties=['slug','name', 'address','description'])
        #geojson = GeoJSON.GeoJSON()
        #string = geojson.encode(dj.decode(node))
        #geojson_queryset=json.loads(string)
        #self.queryset=(geojson_queryset)
        #return self.queryset
        ##return Response(geojson_queryset)
    
    def get(self, request, *args, **kwargs):
        """
        TODO: improve readability and cleanup
        """
        node = Node.objects.published().accessible_to(request.user)
        dj = Django.Django(geodjango="coords", properties=['slug','name', 'address','description'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(node))  
        
        return Response(json.loads(string))

geojson_list = NodeGeojsonList.as_view()


### ------ Images ------ ###


class NodeImageList(CustomDataMixin,generics.ListCreateAPIView):
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
    serializer_class=ImageListSerializer
    serializer_custom_class=ImageAddSerializer
    
    # TODO:
    # create a dedicated serializer
    # which puts added and updated as last attributes
    # removes node_id
    # inserts full url path to where image is located
    
    def get_custom_data(self):
        """ additional request.DATA """
        return {
            'node': self.node.id
        }
    
    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure node exists and store it in an instance attribute
            * change queryset to return only images of current node
        """
        super(NodeImageList, self).initial(request, *args, **kwargs)
        
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
        # return only comments of current node
        self.queryset = Image.objects.filter(node_id=self.node.id).accessible_to(self.request.user)
    
    #def get_queryset(self):
    #    """
    #    Get images of specified existing and published node
    #    or otherwise return 404
    #    """
    #    ## ensure exists
    #    #try:
    #    #    # retrieve slug value from instance attribute kwargs, which is a dictionary
    #    #    slug_value = self.kwargs.get('slug', None)
    #    #    # get node, ensure is published
    #    #    node = Node.objects.published().get(slug=slug_value)
    #    #except Exception:
    #    #    raise Http404(_('Node not found'))
    #    #
    #    #return node.image_set.accessible_to(self.request.user)
    

node_images = NodeImageList.as_view()