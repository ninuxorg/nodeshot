from rest_framework import serializers

from .models import Layer
from nodeshot.core.nodes.serializers import NodeListSerializer


__all__ = [
    'LayerDetailSerializer',
    'LayerListSerializer',
    'LayerNodeListSerializer'
]


class LayerListSerializer(serializers.ModelSerializer):
    """
    Layer list
    """
    details = serializers.HyperlinkedIdentityField(view_name='api_layer_detail', slug_field='slug')
    nodes = serializers.HyperlinkedIdentityField(view_name='api_layer_nodes_list', slug_field='slug')
    geojson = serializers.HyperlinkedIdentityField(view_name='api_layer_nodes_geojson', slug_field='slug')
    
    class Meta:
        model = Layer
        fields= ('name', 'center', 'area', 'details', 'nodes', 'geojson')


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