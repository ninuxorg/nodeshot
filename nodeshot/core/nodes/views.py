from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count

from rest_framework import permissions, authentication, generics

from nodeshot.core.base.mixins import ACLMixin, CustomDataMixin
from nodeshot.core.base.utils import Hider

from .settings import REVERSION_ENABLED
from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *


if REVERSION_ENABLED:
    from nodeshot.core.base.mixins import RevisionCreate, RevisionUpdate

    class NodeListBase(ACLMixin, RevisionCreate, generics.ListCreateAPIView):
        pass

    class NodeDetailBase(ACLMixin, RevisionUpdate, generics.RetrieveUpdateDestroyAPIView):
        pass
else:
    class NodeListBase(ACLMixin, generics.ListCreateAPIView):
        pass

    class NodeDetailBase(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
        pass


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


class NodeList(NodeListBase):
    """
    Retrieve list of all published nodes.

    Parameters:

     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `limit=<n>`: specify number of items per page (defaults to 50)
     * `limit=0`: turns off pagination

    ### POST

    Create a new node. Requires authentication.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Node.objects.published()
    serializer_class = NodeListSerializer
    pagination_serializer_class = PaginatedNodeListSerializer
    paginate_by_param = 'limit'
    paginate_by = 50

    def pre_save(self, obj):
        """ automatically determine user on creation """
        if not obj.id:
            obj.user_id = self.request.user.id

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
            search_query = (
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search)
            )
            # add instructions for search to queryset
            queryset = queryset.filter(search_query)

        return queryset

node_list = NodeList.as_view()


class NodeDetail(NodeDetailBase):
    """
    Retrieve details of specified node. Node must be published and accessible.

    ### DELETE

    Delete specified nodes. Must be authenticated as owner or admin.

    ### PUT & PATCH

    Edit node. Must be authenticated as owner or admin.
    """
    lookup_field = 'slug'
    serializer_class = NodeDetailSerializer
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    queryset = Node.objects.published().select_related('user', 'layer')

node_details = NodeDetail.as_view()


class NodeGeoJSONList(NodeList):
    """
    Retrieve list of all published nodes in GeoJSON format.

    Parameters:

     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `limit=<n>`: specify number of items per page (defaults to 50)
     * `limit=0`: turns off pagination
     * `page=<n>`: show page n
    """
    pagination_serializer_class = PaginatedGeojsonNodeListSerializer
    paginate_by_param = 'limit'
    paginate_by = 50
    serializer_class = NodeGeoSerializer
    post = Hider()

geojson_list = NodeGeoJSONList.as_view()


# -------- Images -------- #


class NodeImageList(CustomDataMixin, generics.ListCreateAPIView):
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
        self.node = get_queryset_or_404(
            Node.objects.published().accessible_to(request.user),
            { 'slug': self.kwargs.get('slug', None) }
        )

        # check permissions on node (for image creation)
        self.check_object_permissions(request, self.node)

        # return only images of current node
        self.queryset = Image.objects.filter(node_id=self.node.id).accessible_to(self.request.user).select_related('node')

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
            { 'slug': self.kwargs.get('slug', None) }
        )

        return super(ImageDetail, self).get_queryset().filter(node=self.node)

node_image_detail = ImageDetail.as_view()


# --------- Status ---------#


class StatusList(generics.ListAPIView):
    """
    Retrieve a list of all the available statuses and their relative icons/colors.
    """
    queryset = Status.objects.all()
    serializer_class = StatusListSerializer

    @method_decorator(cache_page(86400))  # cache for 1 day
    def dispatch(self, *args, **kwargs):
        return super(StatusList, self).dispatch(*args, **kwargs)

status_list = StatusList.as_view()
