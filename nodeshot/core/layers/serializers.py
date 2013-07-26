from django.conf import settings
from rest_framework import serializers, pagination

from .models import Layer

from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.serializers import NodeListSerializer


__all__ = [
    'LayerDetailSerializer',
    'LayerListSerializer',
    'LayerNodeListSerializer',
    'CustomNodeListSerializer',
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

        fields= ('id','slug','name', 'center', 'area', 'details', 'nodes', 'geojson')



class LayerDetailSerializer(LayerListSerializer):
    """
    Layer details
    """
    class Meta:
        model = Layer
        fields = ('name', 'center', 'area', 'zoom', 'is_external',
                  'description', 'text', 'organization', 'website', 'nodes', 'geojson')


class CustomNodeListSerializer(NodeListSerializer):
    
    class Meta:
        model = Node
        fields = [
            'name', 'slug', 'user',
            'coords', 'elev', 'address', 'description'
        ]
        
        if settings.NODESHOT['SETTINGS']['NODE_AREA']:
            fields += ['area']
        
        fields += ['updated', 'added', 'details']
        read_only_fields = ['added', 'updated']


class LayerNodeListSerializer(LayerDetailSerializer):
    """
    Nodes of a Layer
    """
    
    class Meta:
        model = Layer

        fields = ('name', 'description', 'text', 'organization', 'website')    

