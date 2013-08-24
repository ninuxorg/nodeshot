from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


__all__ = [
    'DeviceListSerializer',
    'DeviceDetailSerializer',
    'PaginatedDeviceSerializer',
]

  
class DeviceListSerializer(gis_serializers.GeoModelSerializer):
    """ location geo serializer  """
    
    details = serializers.HyperlinkedIdentityField(view_name='api_device_details')    
    
    class Meta:
        model = Device
        fields = [
            'id', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'firmware', 'os', 'description', 'data',
            'details'
        ]

class DeviceDetailSerializer(DeviceListSerializer):
    
    class Meta:
        model = Device
        fields = [
            'id', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'firmware', 'os', 'description', 'data',
            'routing_protocols',
        ]

class PaginatedDeviceSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = DeviceListSerializer