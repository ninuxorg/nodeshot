from rest_framework import serializers

from .models import Layer
from nodeshot.core.nodes.serializers import NodeListSerializer


__all__ = [
    'LayerDetailSerializer',
    'LayerListSerializer',
    'LayerNodeListSerializer'
]


class LayerListSerializer(serializers.ModelSerializer):
    """ Layer list """
    details = serializers.HyperlinkedIdentityField(view_name='api_layer_details', slug_field='slug')
    nodes = serializers.HyperlinkedIdentityField(view_name='api_layer_nodes_details', slug_field='slug')
    
    class Meta:
        model = Layer
        fields= ('name', 'center', 'area', 'details', 'nodes')


class LayerDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Layer
        fields = ('name', 'center', 'area', 'zoom', 'is_external', 'description', 'organization', 'website')


class LayerNodeListSerializer(LayerDetailSerializer):
    """ Layer nodes """
    nodes = NodeListSerializer(source='node_set')
    
    class Meta:
        model = Layer
        fields = ('name', 'nodes')    