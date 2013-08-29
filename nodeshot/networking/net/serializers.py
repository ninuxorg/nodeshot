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
    'EthernetDetailSerializer',
    'EthernetAddSerializer',
    'WirelessSerializer',
    'WirelessDetailSerializer',
    'WirelessAddSerializer',
    
    'IpSerializer',
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
            'firmware', 'os', 'description',
            'added', 'updated', 'details'
        ]
        read_only_fields = ['added', 'updated']


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
        return EthernetSerializer(interfaces, many=True, context=self.context).data
    
    def get_wireless_interfaces(self, obj):
        user = self.context['request'].user
        interfaces = Wireless.objects.filter(device=obj.id).accessible_to(user)
        return WirelessSerializer(interfaces, many=True, context=self.context).data
    
    class Meta:
        model = Device
        primary_fields = [
            'id', 'access_level', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'firmware', 'os', 'description', 'routing_protocols',
            'added', 'updated'
        ]
        
        if HSTORE_ENABLED:
            primary_fields.insert(primary_fields.index('added'), 'data')
        
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
    
    ip = serializers.SerializerMethodField('get_ip_addresses')
    #ip_url = serializers.HyperlinkedIdentityField(view_name='api_device_ethernet')
    
    if HSTORE_ENABLED:
        data = HStoreDictionaryField(
            required=False,
            label=_('extra data'),
            help_text=_('store extra attributes in JSON string')
        )
    
    def get_ip_addresses(self, obj):
        user = self.context['request'].user
        interfaces = Ip.objects.filter(interface=obj.id).accessible_to(user)
        return IpSerializer(interfaces, many=True, context=self.context).data
    
    class Meta:
        model = Interface
        fields = [
            'id', 'access_level', 'type', 'name',
            'mac', 'mtu', 'tx_rate', 'rx_rate',
            'added', 'updated', 'ip',
        ]
        read_only_fields = ['added', 'updated']
        
        if HSTORE_ENABLED:
            fields.insert(fields.index('added'), 'data')


class EthernetSerializer(InterfaceSerializer):
    class Meta:
        model = Ethernet
        fields = InterfaceSerializer.Meta.fields[:] + [
            'standard', 'duplex'
        ]


class EthernetDetailSerializer(EthernetSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_ethernet_details')
    
    class Meta:
        model = Ethernet
        fields = EthernetSerializer.Meta.fields[:] + ['details']


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


class WirelessDetailSerializer(EthernetSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_wireless_details')
    
    class Meta:
        model = Wireless
        fields = WirelessSerializer.Meta.fields[:] + ['details']


class WirelessAddSerializer(WirelessSerializer):
    class Meta:
        model = Wireless
        fields = WirelessSerializer.Meta.fields[:] + ['device']


# ------ IP ADDRESS ------ #


class IpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ip
        fields = ['address', 'protocol', 'netmask', 'added', 'updated']
        read_only_fields = ['added', 'updated']