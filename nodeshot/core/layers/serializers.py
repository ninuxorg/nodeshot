from rest_framework import serializers,pagination

from .models import Layer
from nodeshot.core.nodes.serializers import NodeListSerializer


__all__ = [
    'LayerDetailSerializer',
    'LayerListSerializer',
    'LayerNodeListSerializer',
    'PaginationSerializer',
    'LinksSerializer',
]


class LinksSerializer(serializers.Serializer):
    
    next = pagination.NextPageField(source='*')
    prev = pagination.PreviousPageField(source='*')


class PaginationSerializer(pagination.BasePaginationSerializer):

    links = LinksSerializer(source='*')  # Takes the page object as the source
    total_results = serializers.Field(source='paginator.count')
    results_field = 'layers'

class LayerListSerializer(serializers.ModelSerializer):
    """
    Layer list
    """
    details = serializers.HyperlinkedIdentityField(view_name='api_layer_detail', slug_field='slug')
    nodes = serializers.HyperlinkedIdentityField(view_name='api_layer_nodes_list', slug_field='slug')
    geojson = serializers.HyperlinkedIdentityField(view_name='api_layer_nodes_geojson', slug_field='slug')
    
    class Meta:
        model = Layer
        fields= ('slug','name', 'center', 'area', 'details', 'nodes', 'geojson')



class LayerDetailSerializer(LayerListSerializer):
    """
    Layer details
    """
    class Meta:
        model = Layer
        fields = ('name', 'center', 'area', 'zoom', 'is_external',
                  'description', 'organization', 'website', 'nodes', 'geojson')


class LayerNodeListSerializer(LayerDetailSerializer):
    """
    Nodes of a Layer
    """
    nodes = NodeListSerializer(source='node_set')
    
    class Meta:
        model = Layer
        fields = ('name', 'nodes')    