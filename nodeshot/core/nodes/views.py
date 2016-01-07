from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q

from rest_framework import permissions, authentication, generics, pagination

from nodeshot.core.base.utils import Hider
from nodeshot.core.base.mixins import ACLMixin
from rest_framework_gis.pagination import GeoJsonPagination

from .permissions import IsOwnerOrReadOnly
from .serializers import *  # noqa
from .models import Node, Status, Image
from .base import ListCreateAPIView, RetrieveUpdateDestroyAPIView


def get_queryset_or_404(queryset, kwargs):
    """
    Checks if object returned by queryset exists
    """
    try:
        return queryset.get(**kwargs)
    except Exception:
        raise Http404(_('Not found'))


class NodeList(ListCreateAPIView):
    """
    Retrieve list of all published nodes.

    Parameters:

     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `layers=<layer1>,<layer2>`: retrieve nodes of specified layers (comma separated)
     * `limit=<n>`: specify number of items per page (defaults to 50)

    ### POST

    Create a new node. Requires authentication.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Node.objects.published()
    serializer_class = NodeListSerializer
    pagination_class = pagination.PageNumberPagination
    paginate_by_param = 'limit'
    paginate_by = 50

    def perform_create(self, serializer):
        """ determine user when node is added """
        if serializer.instance is None:
            serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Optionally restricts the returned nodes
        by filtering against a `search` query parameter in the URL.
        """
        # retrieve all nodes which are published and accessible to current user
        # and use joins to retrieve related fields
        queryset = super(NodeList, self).get_queryset().select_related('status', 'user', 'layer')
        # query string params
        search = self.request.query_params.get('search', None)
        layers = self.request.query_params.get('layers', None)
        if search is not None:
            search_query = (
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search)
            )
            # add instructions for search to queryset
            queryset = queryset.filter(search_query)
        if layers is not None:
            # look for nodes that are assigned to the specified layers
            queryset = queryset.filter(Q(layer__slug__in=layers.split(',')))
        return queryset

node_list = NodeList.as_view()


class NodeDetail(RetrieveUpdateDestroyAPIView):
    """
    Retrieve details of specified node. Node must be published and accessible.

    ### DELETE

    Delete specified nodes. Must be authenticated as owner or admin.

    ### PUT & PATCH

    Edit node. Must be authenticated as owner or admin.
    """
    lookup_field = 'slug'
    serializer_class = NodeSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    queryset = Node.objects.published().select_related('status', 'user', 'layer')

node_details = NodeDetail.as_view()


class NodeGeoJsonList(NodeList):
    """
    Retrieve list of all published nodes in GeoJSON format.

    Parameters:

     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `layers=<layer1>,<layer2>`: retrieve nodes of specified layers
     * `limit=<n>`: specify number of items per page (show all by default)
     * `page=<n>`: show page n
    """
    pagination_class = GeoJsonPagination
    paginate_by_param = 'limit'
    paginate_by = 0
    serializer_class = NodeGeoJsonSerializer
    post = Hider()

geojson_list = NodeGeoJsonList.as_view()


# -------- Images -------- #


class NodeImageList(generics.ListCreateAPIView):
    """
    Retrieve a list of images of the specified node.
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
    serializer_class = ImageSerializer
    permission_classes = (IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(node=self.node)

    def get_queryset(self):
        # return images of current node
        return Image.objects.filter(node=self.node)\
                            .accessible_to(self.request.user)\
                            .select_related('node')

    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure node exists and store it in an instance attribute
            * change queryset to return only images of current node
        """
        super(NodeImageList, self).initial(request, *args, **kwargs)
        # ensure node exists
        self.node = get_queryset_or_404(
            Node.objects.published().accessible_to(request.user),
            {'slug': self.kwargs['slug']}
        )
        # check permissions on node (for image creation)
        self.check_object_permissions(request, self.node)

node_images = NodeImageList.as_view()


class ImageDetail(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve details of specified image.

    ### DELETE

    Delete specified nodes. Must be authenticated as owner or admin.

    ### PUT & PATCH

    Edit image.

    **Permissions:** only owner of a node can edit.

    Example of **JSON** representation that should be sent:

        {
            "description": "image caption",
            "order": 3,
            "access_level": "public"
        }
    """
    queryset = Image.objects.all()
    serializer_class = ImageEditSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    lookup_field = 'pk'

    def get_queryset(self):
        self.node = get_queryset_or_404(
            Node.objects.published().accessible_to(self.request.user),
            {'slug': self.kwargs.get('slug', None)}
        )
        return super(ImageDetail, self).get_queryset().filter(node=self.node)

node_image_detail = ImageDetail.as_view()


# --------- Status ---------#


class StatusList(generics.ListAPIView):
    """
    Retrieve a list of all the available statuses and their relative icons/colors.
    """
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    @method_decorator(cache_page(86400))  # cache for 1 day
    def dispatch(self, *args, **kwargs):
        return super(StatusList, self).dispatch(*args, **kwargs)

status_list = StatusList.as_view()


# --------- Utils ---------#

from rest_framework.decorators import api_view
from rest_framework.response import Response
from geojson_elevation.backends.google import elevation

from .settings import ELEVATION_API_KEY, ELEVATION_DEFAULT_SAMPLING


@api_view(('GET',))
def elevation_profile(request, format=None):
    """
    Proxy to google elevation API but returns GeoJSON
    (unless "original" parameter is passed, in which case the original response is returned).

    For input parameters read:
    https://developers.google.com/maps/documentation/elevation/
    """
    if format is None:
        format = 'json'

    path = request.query_params.get('path')
    if not path:
        return Response({'detail': _('missing required path argument')}, status=400)

    return Response(elevation(path,
                              api_key=ELEVATION_API_KEY,
                              sampling=ELEVATION_DEFAULT_SAMPLING))
