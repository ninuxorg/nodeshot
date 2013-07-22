from django.conf import settings
from rest_framework import serializers,pagination

from nodeshot.core.layers.models import Layer
from .models import Node,Image


__all__ = [
    'NodeListSerializer',
    'NodeDetailSerializer',
    'NodePaginationSerializer',
    'LinksSerializer',
    'GeojsonNodeListSerializer',
    'ImageListSerializer',
    'ImageAddSerializer'
    
]
  
  
class LinksSerializer(serializers.Serializer):
    
    next = pagination.NextPageField(source='*')
    prev = pagination.PreviousPageField(source='*')


class NodePaginationSerializer(pagination.BasePaginationSerializer):

    links = LinksSerializer(source='*')  # Takes the page object as the source
    total_results = serializers.Field(source='paginator.count')
    results_field = 'nodes'


class GeojsonNodeListSerializer(serializers.Serializer):
    
    #user= serializers.Field(source='user.username')
    #layer = serializers.Field(source='layer.name')
    
    #details = serializers.HyperlinkedIdentityField(view_name='api_node_details', slug_field='slug')
    
    class Meta:
        model = Node
        #crs=serializers.Field()
        #type=serializers.Field()
        #features=serializers.Field()

    #    
    #    if settings.NODESHOT['SETTINGS']['NODE_AREA']:
    #        fields += ['area']
    #    
    #    fields += ['details']
        
        #fields = ('layer', 'name', 'slug', 'user', 'coords', 'elev', 'details')


class NodeListSerializer(serializers.ModelSerializer):
    
    user= serializers.Field(source='user.username')
    #layer = serializers.Field(source='layer.name')
    
    details = serializers.HyperlinkedIdentityField(view_name='api_node_details', slug_field='slug')
    
    class Meta:
        model = Node
        fields = ['layer', 'name', 'slug', 'user', 'coords', 'elev', 'address']
        
        if settings.NODESHOT['SETTINGS']['NODE_AREA']:
            fields += ['area']
        
        fields += ['details']
        
        #fields = ('layer', 'name', 'slug', 'user', 'coords', 'elev', 'details')

  
class NodeDetailSerializer(serializers.ModelSerializer):
    """ node detail """
    #Added user and layer so tht explicit names are displayed instead of ID
    user = serializers.Field(source='user.username')
    layer = serializers.Field(source='layer.name')
    images = serializers.HyperlinkedIdentityField(view_name='api_node_images', slug_field='slug')
    
    if 'nodeshot.community.participation' in settings.NODESHOT['API']['APPS_ENABLED']:
        comments = serializers.HyperlinkedIdentityField(view_name='api_node_comments', slug_field='slug')
    
    class Meta:
        model = Node
        fields = ['layer', 'name', 'slug', 'user', 'coords', 'elev','address']
        
        if settings.NODESHOT['SETTINGS']['NODE_AREA']:
            fields += ['area']
            
        fields += ['images']
        
        if 'nodeshot.community.participation' in settings.NODESHOT['API']['APPS_ENABLED']:
            fields += ['comments']
            
        fields += ['comments']
        
class ImageListSerializer(serializers.ModelSerializer):
    
    user= serializers.Field(source='user.username')
        
    class Meta:
        model = Image
        fields = ('file', 'description', 'added', 'order')
        read_only_fields = ('added',)


class ImageAddSerializer(serializers.ModelSerializer):
    
    user= serializers.Field(source='user.username')
    #layer = serializers.Field(source='layer.name')
        
    class Meta:
        model = Image
        fields = ('node', 'file', 'description', 'order')
