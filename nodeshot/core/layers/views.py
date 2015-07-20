from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import permissions, authentication, pagination
from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination

from nodeshot.core.base.utils import Hider
from nodeshot.core.nodes.views import NodeList, NodeGeoJsonList
from nodeshot.core.nodes.serializers import NodeGeoJsonSerializer

from .models import Layer
from .serializers import *  # noqa
from .base import ListCreateAPIView, RetrieveUpdateAPIView


class LayerList(ListCreateAPIView):
    """
    Retrieve list of all layers.

    ### POST

    Create new layer if authorized (admins and allowed users only).
    """
    queryset = Layer.objects.published()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class = LayerListSerializer
    pagination_serializer = pagination.PageNumberPagination
    paginate_by_param = 'limit'
    paginate_by = 0

layer_list = LayerList.as_view()


class LayerDetail(RetrieveUpdateAPIView):
    """
    Retrieve details of specified layer.

    ### PUT & PATCH

    Edit specified layer
    """
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Layer.objects.published()
    serializer_class = LayerDetailSerializer
    lookup_field = 'slug'

layer_detail = LayerDetail.as_view()


class LayerNodeListMixin(object):
    layer = None

    def get_layer(self):
        """ retrieve layer from DB """
        if self.layer:
            return
        try:
            self.layer = Layer.objects.get(slug=self.kwargs['slug'])
        except Layer.DoesNotExist:
            raise Http404(_('Layer not found'))

    def get_queryset(self):
        """ extend parent class queryset by filtering nodes of the specified layer """
        self.get_layer()
        return super(LayerNodeListMixin, self).get_queryset().filter(layer_id=self.layer.id)

    def get_nodes(self, request, *args, **kwargs):
        """ this method might be overridden by other modules (eg: nodeshot.interop.sync) """
        # ListSerializerMixin.list returns a serializer object
        return (self.list(request, *args, **kwargs)).data

    def get(self, request, *args, **kwargs):
        """ Retrieve list of nodes of the specified layer """
        self.get_layer()
        # get nodes of layer
        nodes = self.get_nodes(request, *args, **kwargs)
        return Response(nodes)

    post = Hider()


class LayerNodesList(LayerNodeListMixin, NodeList):
    """
    Retrieve list of nodes of the specified layer

    Parameters:

     * `search=<word>`: search <word> in name of nodes of specified layer
     * `limit=<n>`: specify number of items per page (defaults to 40)
    """
    pass

nodes_list = LayerNodesList.as_view()


class LayerNodesGeoJsonList(LayerNodeListMixin, NodeGeoJsonList):
    """
    Retrieve list of nodes of the specified layer in GeoJson format.

    Parameters:

     * `search=<word>`: search <word> in name, slug, description and address of nodes
     * `limit=<n>`: specify number of items per page (show all by default)
    """
    pagination_serializer = GeoJsonPagination
    paginate_by_param = 'limit'
    paginate_by = 0
    serializer_class = NodeGeoJsonSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieve list of nodes of the specified layer in GeoJSON format. """
        # overwritten just to tweak the docstring for auto documentation purposes
        return super(LayerNodesGeoJsonList, self).get(request, *args, **kwargs)

nodes_geojson_list = LayerNodesGeoJsonList.as_view()
