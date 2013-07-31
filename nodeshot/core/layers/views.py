import simplejson as json
from vectorformats.Formats import Django, GeoJSON

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from nodeshot.core.nodes.views import NodeList

from .models import Layer
from .serializers import *


class LayerList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list of layers.
    
    ### POST
    
    Create new layer if authorized (admins and allowed users only).
    """
    model= Layer
    serializer_class= LayerListSerializer
    queryset = Layer.objects.published()
    pagination_serializer_class = PaginationSerializer
    paginate_by_param = 'limit'
    paginate_by = None
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

layer_list = LayerList.as_view()


class LayerDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve details of specified layer.
    """
    model= Layer
    serializer_class= LayerDetailSerializer
    queryset = Layer.objects.published()
    lookup_field = 'slug'

layer_detail = LayerDetail.as_view()

    
class LayerNodesList(NodeList):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer
    
    Parameters:
    
     * `search=<word>`: search <word> in name of nodes of specified layer
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    """
    #model = Layer
    #serializer_class = CustomNodeListSerializer
    #queryset = Layer.objects.published()
    #lookup_field = 'slug'
    
    def get_queryset(self):
        try:
            self.layer = Layer.objects.get(slug=self.kwargs['slug'])
        except Layer.DoesNotExist:
            raise Http404(_('Layer not found'))
        
        return super(LayerNodesList, self).get_queryset().filter(layer_id=self.layer.id)
    
    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        if not self.allow_empty and not self.object_list:
            warnings.warn(
                'The `allow_empty` parameter is due to be deprecated. '
                'To use `allow_empty=False` style behavior, You should override '
                '`get_queryset()` and explicitly raise a 404 on empty querysets.',
                PendingDeprecationWarning
            )
            class_name = self.__class__.__name__
            error_msg = self.empty_error % {'class_name': class_name}
            raise Http404(error_msg)

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)
        
        return serializer
    
    def get(self, request, *args, **kwargs):
        """ custom structure """
        nodes = self.list(request, *args, **kwargs)
        
        content = LayerNodeListSerializer(self.layer, context=self.get_serializer_context()).data
        content['nodes'] = nodes.data
        
        return Response(content)

nodes_list = LayerNodesList.as_view()


class LayerAllNodesGeojsonList(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer in GeoJSON format.
    """
    
    model = Layer
    
    def get(self, request, *args, **kwargs):
        """
        Get nodes of specified existing and published layer
        or otherwise return 404
        Outputs nodes in geojson format
        TODO: improve readability and cleanup
        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            layer = Layer.objects.get(slug=slug_value)
        except Exception:
            raise Http404(_('Layer not found'))
        
        nodes = layer.node_set.published().accessible_to(request.user)
        dj = Django.Django(geodjango="coords", properties=['slug', 'name', 'address', 'description'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(nodes))  
        
        return Response(json.loads(string))

nodes_geojson_list = LayerAllNodesGeojsonList.as_view()


class LayerGeojsonList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve layers in GeoJSON format.
    """
    paginate_by_param = 'results'
    
    def get(self, request, *args, **kwargs):
        """
        TODO: improve readability and cleanup
        """
        #select only layers with field 'area' populated. Otherwise VectorFormats throws an exception
        layer = Layer.objects.published().exclude(area__isnull=True)
        dj = Django.Django(geodjango="area", properties=['slug','name', 'id'])
        geojson = GeoJSON.GeoJSON()
        string = geojson.encode(dj.decode(layer))  
        
        return Response(json.loads(string))

layers_geojson_list = LayerGeojsonList.as_view()