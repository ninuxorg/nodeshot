from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from nodeshot.core.base.mixins import ACLMixin, CustomDataMixin

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *

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
    
     * `search=<word>`: search <word> in name of nodes
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    
    ### POST
    
    Create a new node.
    
    **Permissions:** restricted to authenticated users only.
    
    Example of **JSON** representation that should be sent:
    
    <pre>{
        "name": "Fusolab Rome", 
        "slug": "fusolab", 
        "coords": [41.872041927700003, 12.582239191899999], 
        "elev": 80.0, 
        "address": "", 
        "description": "Fusolab test", 
        "layer": 1
    }</pre>
    
    **Required Fields**:
    
     * name
     * slug
     * coords
     * layer (if layer app installed)
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
        queryset = super(NodeList, self).get_queryset().select_related('layer', 'status', 'user')
        
        # retrieve value of querystring parameter "search"
        search = self.request.QUERY_PARAMS.get('search', None)
        
        if search is not None:
            # add instructions for search to queryset
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
node_list = NodeList.as_view()
    
    
class NodeDetail(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    ### GET
    
    Retrieve details of specified node
    
    ### DELETE
    
    Delete specified nodes. Must be authenticated as owner or admin.
    
    ### PUT & PATCH
    
    Edit node.
    
    **Permissions:** only owner of a node can edit.
    
    Example of **JSON** representation that should be sent:
    
    <pre>{
        "name": "Fusolab Rome", 
        "slug": "fusolab", 
        "user": "romano", 
        "coords": [41.872041927700003, 12.582239191899999], 
        "elev": 80.0, 
        "address": "", 
        "description": "Fusolab test", 
        "access_level": "public",
        "layer": 1
    }</pre>
    
    **Required Fields**:
    
     * name
     * slug
     * coords
     * layer (if layer app installed)
    """
    lookup_field = 'slug'
    model = Node
    serializer_class = NodeDetailSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    queryset = Node.objects.published().select_related('user', 'layer')

node_details = NodeDetail.as_view()


class NodeGeojsonList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve nodes in GeoJSON format.
    """
    
    def get(self, request, *args, **kwargs):
        """
        TODO: improve readability and cleanup
        """
        node = Node.objects.published().accessible_to(request.user)
        dj = Django.Django(geodjango="coords", properties=['slug', 'name', 'address', 'description'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(node))  
        
        return Response(json.loads(string))

geojson_list = NodeGeojsonList.as_view()


### ------ Images ------ ###


class NodeImageList(CustomDataMixin, generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a list of image of the specified node.
    Node must exist and be published.
    
    ### POST
    
    Upload a new image.
    
    **Permissions:** only owner of a node can upload images.
    
    **Fields**:
    
     * `file`: binary file of the image, accepted file types are JPEG, PNG and GIF - **required**
     * `description`: description / caption of the image
     * `order`: order of the image, leave blank to set as last
     * `access_level`: determines who can see the image, defaults to public
    
    ### How do I upload an image?
    
    Set the content-type as **"multipart-formdata"** and send the file param as a binary stream.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    model = Image
    serializer_class = ImageListSerializer
    serializer_custom_class = ImageAddSerializer
    permission_classes = (IsOwnerOrReadOnly, )
    
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
        self.node = get_queryset_or_404(Node.objects.published().accessible_to(request.user), { 'slug': self.kwargs.get('slug', None) })
        
        # check permissions on node (for image creation)
        self.check_object_permissions(request, self.node)
        
        # return only comments of current node
        self.queryset = Image.objects.filter(node_id=self.node.id).accessible_to(self.request.user).select_related('node')

node_images = NodeImageList.as_view()


class ImageDetail(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    ### GET
    
    Retrieve details of specified image
    
    ### DELETE
    
    Delete specified nodes. Must be authenticated as owner or admin.
    
    ### PUT & PATCH
    
    Edit image.
    
    **Permissions:** only owner of a node can edit.
    
    Example of **JSON** representation that should be sent:
    
    <pre>{
        "description": "image caption", 
        "order": 3,
        "access_level": "public"
    }</pre>
    """
    model = Image
    queryset = Image.objects.all()
    serializer_class = ImageEditSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    lookup_field = 'pk'
    
    def get_queryset(self):
        
        self.node = get_queryset_or_404(Node.objects.published().accessible_to(self.request.user), {
            'slug': self.kwargs.get('slug', None)
        })
        
        return super(ImageDetail, self).get_queryset().filter(node=self.node)
    

node_image_detail = ImageDetail.as_view()


### ------ Status ------ ###


class StatusList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve all the status and their relative icons.
    """
    model = Status
    serializer_class = StatusListSerializer
    
    @method_decorator(cache_page(86400))  # cache for 1 day
    def dispatch(self, *args, **kwargs):
        return super(StatusList, self).dispatch(*args, **kwargs)
    
status_list = StatusList.as_view()