from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


HSTORE_ENABLED = settings.NODESHOT['SETTINGS'].get('HSTORE', True)

if HSTORE_ENABLED:
    from nodeshot.core.base.fields import HStoreDictionaryField


__all__ = [
    'DeviceListSerializer',
    'DeviceDetailSerializer',
    'DeviceAddSerializer',
    'NodeDeviceListSerializer',
    'PaginatedDeviceSerializer',
    'PaginatedNodeDeviceSerializer',
]

  
class DeviceListSerializer(gis_serializers.GeoModelSerializer):
    """ location geo serializer  """
    
    node = serializers.Field(source='node.slug')
    type = serializers.WritableField(source='get_type_display', label=_('type'))
    status = serializers.Field(source='get_status_display')
    details = serializers.HyperlinkedIdentityField(view_name='api_device_details')    
    
    class Meta:
        model = Device
        fields = [
            'id', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'firmware', 'os', 'description', 'details'
        ]


class DeviceDetailSerializer(DeviceListSerializer):
    
    access_level = serializers.Field(source='get_access_level_display')
    
    if HSTORE_ENABLED:
        data = HStoreDictionaryField(
            required=False,
            label=_('extra data'),
            help_text=_('store extra attributes in JSON string')
        )
    
    class Meta:
        model = Device
        fields = [
            'id', 'access_level', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'firmware', 'os', 'description', 'routing_protocols']
        
        if HSTORE_ENABLED:
            fields += ['data']


class NodeDeviceListSerializer(DeviceDetailSerializer):
    """ serializer to list devices of a node """
    class Meta:
        model = Device
        fields = DeviceDetailSerializer.Meta.fields[:] + ['details']


class DeviceAddSerializer(NodeDeviceListSerializer):
    """ Serializer for Device Creation """
    node = serializers.WritableField(source='node_id')
    type = serializers.WritableField(source='type')
    details = serializers.HyperlinkedIdentityField(view_name='api_device_details') 


class PaginatedDeviceSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = DeviceListSerializer


class PaginatedNodeDeviceSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = NodeDeviceListSerializer