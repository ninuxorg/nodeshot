from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from rest_framework import authentication, generics

from nodeshot.core.base.mixins import ACLMixin
from nodeshot.core.nodes.models import Node

from .serializers import *
from .models import *


class LinkList(ACLMixin, generics.ListAPIView):
    """
    Retrieve link list according to user access level

    Parameters:

     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Link.objects.all()
    serializer_class = LinkListSerializer
    pagination_serializer_class = PaginatedLinkSerializer
    paginate_by_param = 'limit'
    paginate_by = 40

link_list = LinkList.as_view()


class LinkGeoJSONList(ACLMixin, generics.ListAPIView):
    """
    Retrieve link list in GeoJSON format
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Link.objects.all()
    serializer_class = LinkListGeoJSONSerializer

link_geojson_list = LinkGeoJSONList.as_view()


class LinkDetails(ACLMixin, generics.RetrieveAPIView):
    """
    Retrieve details of specified link
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Link.objects.all()
    serializer_class = LinkDetailSerializer

link_details = LinkDetails.as_view()


class LinkGeoJSONDetails(LinkDetails):
    """
    Get link details in GeoJSON format
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Link.objects.all()
    serializer_class = LinkDetailGeoJSONSerializer

link_geojson_details = LinkDetails.as_view()


class NodeLinkList(generics.ListAPIView):
    """
    Retrieve links of specified node according to user access level.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class = LinkDetailSerializer

    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure node exists and store it in an instance attribute
            * change queryset to return only links of current node
        """
        super(NodeLinkList, self).initial(request, *args, **kwargs)
        # ensure node exists
        try:
            self.node = Node.objects.published()\
                                    .accessible_to(request.user)\
                                    .get(slug=self.kwargs.get('slug', None))
        except Node.DoesNotExist:
            raise Http404(_('Node not found.'))
        # check permissions on node (for link creation)
        self.check_object_permissions(request, self.node)
        # return only links of current node
        self.queryset = Link.objects.select_related('node')\
                                    .accessible_to(self.request.user)\
                                    .filter(Q(node_a_id=self.node.id) |
                                            Q(node_b_id=self.node.id))

node_link_list = NodeLinkList.as_view()
