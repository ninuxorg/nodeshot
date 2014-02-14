from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import pagination, serializers
from rest_framework.reverse import reverse
from rest_framework_gis import serializers as gis_serializers

from nodeshot.core.base.serializers import DynamicRelationshipsMixin

from .models import *


__all__ = [
    'LinkListSerializer',
    'LinkDetailSerializer',
    'LinkListGeoJSONSerializer',
    'LinkDetailGeoJSONSerializer',
    'PaginatedLinkSerializer',
]

  
class LinkListSerializer(gis_serializers.GeoModelSerializer):
    """ location serializer  """
    
    quality = serializers.Field(source='quality')
    details = serializers.HyperlinkedIdentityField(view_name='api_link_details')
    
    class Meta:
        model = Link
        fields = ['id', 'line', 'quality', 'details']


class LinkListGeoJSONSerializer(LinkListSerializer, gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'line'
        fields = LinkListSerializer.Meta.fields[:]


class LinkDetailSerializer(DynamicRelationshipsMixin, LinkListSerializer):
    
    access_level = serializers.Field(source='get_access_level_display')
    status = serializers.Field(source='get_status_display')
    type = serializers.Field(source='get_type_display')
    node_a_name = serializers.Field(source='node_a_name')
    node_b_name = serializers.Field(source='node_b_name')
    interface_a_mac = serializers.Field(source='interface_a_mac')
    interface_b_mac = serializers.Field(source='interface_b_mac')
    relationships = serializers.SerializerMethodField('get_relationships')
    
    _relationships = {
        'node_a': ('api_node_details', 'node_a_slug'),
        'node_b': ('api_node_details', 'node_b_slug'),
    }

    class Meta:
        model = Link
        fields = [
            'id', 
            'node_a_name', 'node_b_name',
            'interface_a_mac', 'interface_b_mac',
            'access_level', 'status', 'type', 'line', 
            'quality', 'metric_type', 'metric_value',
            'max_rate', 'min_rate', 'dbm', 'noise',
            'first_seen', 'last_seen',
            'added', 'updated', 'relationships'
        ]


class LinkDetailGeoJSONSerializer(LinkDetailSerializer, gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'line'
        fields = LinkDetailSerializer.Meta.fields[:]


#class LinkAddSerializer(NodeLinkListSerializer):
#    """ Serializer for Link Creation """
#    node = serializers.WritableField(source='node_id')
#    type = serializers.WritableField(source='type')
#    details = serializers.HyperlinkedIdentityField(view_name='api_link_details') 


class PaginatedLinkSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = LinkListSerializer


#class PaginatedNodeLinkSerializer(pagination.PaginationSerializer):
#    class Meta:
#        object_serializer_class = NodeLinkListSerializer