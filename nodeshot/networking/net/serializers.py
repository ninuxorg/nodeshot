from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from nodeshot.core.base.fields import MacAddressField

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
    'EthernetSerializer',
    'EthernetAddSerializer',
    'WirelessSerializer',
    'WirelessAddSerializer'
]


# ------ DEVICES ------ #

  
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
    
    ethernet = serializers.SerializerMethodField('get_ethernet_interfaces')
    ethernet_url = serializers.HyperlinkedIdentityField(view_name='api_device_ethernet')
    
    wireless = serializers.SerializerMethodField('get_wireless_interfaces')
    wireless_url = serializers.HyperlinkedIdentityField(view_name='api_device_wireless')
    
    if HSTORE_ENABLED:
        data = HStoreDictionaryField(
            required=False,
            label=_('extra data'),
            help_text=_('store extra attributes in JSON string')
        )
    
    def get_ethernet_interfaces(self, obj):
        user = self.context['request'].user
        interfaces = Ethernet.objects.filter(device=obj.id).accessible_to(user)
        return EthernetSerializer(interfaces, many=True).data
    
    def get_wireless_interfaces(self, obj):
        user = self.context['request'].user
        interfaces = Wireless.objects.filter(device=obj.id).accessible_to(user)
        return WirelessSerializer(interfaces, many=True).data
    
    class Meta:
        model = Device
        primary_fields = [
            'id', 'access_level', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'firmware', 'os', 'description', 'routing_protocols']
        
        if HSTORE_ENABLED:
            primary_fields += ['data']
        
        secondary_fields = [
            'ethernet', 'ethernet_url',
            'wireless', 'wireless_url'
        ]
        
        fields = primary_fields + secondary_fields


class NodeDeviceListSerializer(DeviceDetailSerializer):
    """ serializer to list devices of a node """
    class Meta:
        model = Device
        fields = DeviceDetailSerializer.Meta.primary_fields[:] + ['details']


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


# ------ INTERFACES ------ #


class InterfaceSerializer(serializers.ModelSerializer):
    """ Base Interface Serializer Class """
    access_level = serializers.Field(source='get_access_level_display')
    mac = MacAddressField(label=_('mac address'))
    type = serializers.Field(source='get_type_display', label=_('type'))
    
    if HSTORE_ENABLED:
        data = HStoreDictionaryField(
            required=False,
            label=_('extra data'),
            help_text=_('store extra attributes in JSON string')
        )
    
    class Meta:
        model = Interface
        fields = [
            'id', 'access_level', 'type', 'name',
            'mac', 'mtu', 'tx_rate', 'rx_rate'
        ]
        
        if HSTORE_ENABLED:
            fields += ['data']


class EthernetSerializer(InterfaceSerializer):
    class Meta:
        model = Ethernet
        fields = InterfaceSerializer.Meta.fields[:] + [
            'standard', 'duplex'
        ]


class EthernetAddSerializer(EthernetSerializer):
    class Meta:
        model = Ethernet
        fields = EthernetSerializer.Meta.fields[:] + ['device']


class WirelessSerializer(InterfaceSerializer):
    class Meta:
        model = Wireless
        fields = InterfaceSerializer.Meta.fields[:] + [
            'mode', 'standard', 'channel',
            'channel_width', 'output_power', 'dbm', 'noise',
        ]


class WirelessAddSerializer(WirelessSerializer):
    class Meta:
        model = Wireless
        fields = WirelessSerializer.Meta.fields[:] + ['device']