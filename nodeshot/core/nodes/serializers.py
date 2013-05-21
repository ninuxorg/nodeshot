from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import serializers

from nodeshot.core.layers.models import Layer
from .models import Node


__all__ = [
    'NodeListSerializer',
    'NodeDetailSerializer'
]


#class UserSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = User
#        fields = ('id', 'username')


class NodeListSerializer(serializers.ModelSerializer):
    user= serializers.Field(source='user.username')
    layer = serializers.Field(source='layer.name')
    
    details = serializers.HyperlinkedIdentityField(view_name='api_node_details', slug_field='slug')
    
    class Meta:
        model = Node
        #fields = ['layer', 'name', 'slug', 'user', 'coords', 'elev']
        #
        #if settings.NODESHOT['SETTINGS']['NODE_AREA']:
        #    fields += ['area']
        #
        #fields += ['details']
        
        fields = ('layer', 'name', 'slug', 'user', 'coords', 'elev', 'details')

  
class NodeDetailSerializer(serializers.ModelSerializer):
    """ node detail """
    
    class Meta:
        model = Node
        fields = ['layer', 'name', 'slug', 'user', 'coords', 'elev']
        
        if settings.NODESHOT['SETTINGS']['NODE_AREA']:
            fields += ['area']
