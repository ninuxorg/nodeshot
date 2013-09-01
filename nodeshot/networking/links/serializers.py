from django.conf import settings
from django.utils.translation import ugettext_lazy as _
#from django.core.exceptions import ValidationError

from rest_framework import pagination, serializers
#from rest_framework.reverse import reverse
from rest_framework_gis import serializers as gis_serializers

from .models import *

from nodeshot.core.base.fields import HStoreDictionaryField


__all__ = [
    'LinkListSerializer',
    'LinkDetailSerializer',
    #'LinkAddSerializer',
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


class LinkDetailSerializer(LinkListSerializer):
    
    access_level = serializers.Field(source='get_access_level_display')
    status = serializers.Field(source='get_status_display')
    type = serializers.Field(source='get_type_display')
    
    data = HStoreDictionaryField(
        required=False,
        label=_('extra data'),
        help_text=_('store extra attributes in JSON string')
    )

    class Meta:
        model = Link
        fields = [
            'id', 'access_level', 'status', 'type', 'line', 
            'quality', 'metric_type', 'metric_value',
            'tx_rate', 'rx_rate', 'dbm', 'noise',
            'added', 'updated'
        ]


class LinkDetailGeoJSONSerializer(LinkDetailSerializer, gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'line'
        fields = LinkDetailSerializer.Meta.fields[:]


#class NodeLinkListSerializer(LinkDetailSerializer):
#    """ serializer to list links of a node """
#    class Meta:
#        model = Link
#        fields = LinkDetailSerializer.Meta.primary_fields[:] + ['details']


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