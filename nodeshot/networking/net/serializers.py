from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from rest_framework import pagination, serializers
from rest_framework.reverse import reverse
from rest_framework_gis import serializers as gis_serializers

from .models import *
from .models.choices import INTERFACE_TYPES
from .fields import MacAddressField, IPAddressField, IPNetworkField

from rest_framework_hstore.fields import HStoreField


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
    
    'BridgeSerializer',
    'BridgeDetailSerializer',
    'BridgeAddSerializer',
    
    'TunnelSerializer',
    'TunnelDetailSerializer',
    'TunnelAddSerializer',
    
    'VlanSerializer',
    'VlanDetailSerializer',
    'VlanAddSerializer',
    
    'VapSerializer',
    
    'IpSerializer',
    'IpDetailSerializer',
    'IpAddSerializer'
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
            'os', 'os_version', 'description',
            'first_seen', 'last_seen',
            'added', 'updated', 'details'
        ]
        read_only_fields = [
            'first_seen', 'last_seen',
            'added', 'updated'
        ]


class DeviceDetailSerializer(DeviceListSerializer):
    
    access_level = serializers.Field(source='get_access_level_display')
    
    routing_protocols_named = serializers.RelatedField(source='routing_protocols', many=True)
    
    ethernet = serializers.SerializerMethodField('get_ethernet_interfaces')
    ethernet_url = serializers.HyperlinkedIdentityField(view_name='api_device_ethernet')
    
    wireless = serializers.SerializerMethodField('get_wireless_interfaces')
    wireless_url = serializers.HyperlinkedIdentityField(view_name='api_device_wireless')
    
    bridge = serializers.SerializerMethodField('get_bridge_interfaces')
    bridge_url = serializers.HyperlinkedIdentityField(view_name='api_device_bridge')
    
    tunnel = serializers.SerializerMethodField('get_tunnel_interfaces')
    tunnel_url = serializers.HyperlinkedIdentityField(view_name='api_device_tunnel')
    
    vlan = serializers.SerializerMethodField('get_vlan_interfaces')
    vlan_url = serializers.HyperlinkedIdentityField(view_name='api_device_vlan')
    
    data = HStoreField(
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
    
    def get_bridge_interfaces(self, obj):
        user = self.context['request'].user
        interfaces = Bridge.objects.filter(device=obj.id).accessible_to(user)
        return BridgeSerializer(interfaces, many=True, context=self.context).data
    
    def get_tunnel_interfaces(self, obj):
        user = self.context['request'].user
        interfaces = Tunnel.objects.filter(device=obj.id).accessible_to(user)
        return TunnelSerializer(interfaces, many=True, context=self.context).data
    
    def get_vlan_interfaces(self, obj):
        user = self.context['request'].user
        interfaces = Vlan.objects.filter(device=obj.id).accessible_to(user)
        return VlanSerializer(interfaces, many=True, context=self.context).data
    
    class Meta:
        model = Device
        primary_fields = [
            'id', 'access_level', 'node', 'name', 'type', 'status',
            'location', 'elev',
            'os', 'os_version', 'description',
            'routing_protocols', 'routing_protocols_named',
            'first_seen', 'last_seen', 'data',
            'added', 'updated'
        ]
        
        secondary_fields = [
            'ethernet', 'ethernet_url',
            'wireless', 'wireless_url',
            'bridge', 'bridge_url',
            'tunnel', 'tunnel_url',
            'vlan', 'vlan_url'
        ]
        
        fields = primary_fields + secondary_fields
        read_only_fields = [
            'added', 'updated',
            'first_seen', 'last_seen',
        ]


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
    
    tx_rate = serializers.Field()
    rx_rate = serializers.Field()
    
    ip = serializers.SerializerMethodField('get_ip_addresses')
    ip_url = serializers.HyperlinkedIdentityField(view_name='api_interface_ip')
    
    data = HStoreField(
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
            'data', 'added', 'updated', 'ip_url', 'ip',
        ]
        read_only_fields = ['added', 'updated']


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
        read_only_fields = ('added', 'updated')


class EthernetAddSerializer(EthernetSerializer):
    class Meta:
        model = Ethernet
        fields = EthernetSerializer.Meta.fields[:] + ['device']
        read_only_fields = ('added', 'updated')


class VapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vap
        fields = ['essid', 'bssid', 'encryption']


class WirelessSerializer(InterfaceSerializer):
    vap = VapSerializer(source='vap_set', many=True, read_only=True)
    
    class Meta:
        model = Wireless
        fields = InterfaceSerializer.Meta.fields[:] + [
            'mode', 'standard', 'channel',
            'channel_width', 'output_power', 'dbm', 'noise', 'vap'
        ]


class WirelessDetailSerializer(WirelessSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_wireless_details')
    
    class Meta:
        model = Wireless
        fields = WirelessSerializer.Meta.fields[:] + ['details']
        read_only_fields = ('added', 'updated')


class WirelessAddSerializer(WirelessSerializer):
    class Meta:
        model = Wireless
        fields = WirelessSerializer.Meta.fields[:] + ['device']
        read_only_fields = ('added', 'updated')


from .models.interfaces.bridge import validate_bridged_interfaces

class BridgeSerializer(InterfaceSerializer):
    
    interfaces = serializers.PrimaryKeyRelatedField(many=True, required=True)
    interfaces_links = serializers.SerializerMethodField('get_interfaces_links')
    
    def get_interfaces_links(self, obj):
        user = self.context['request'].user
        links = []
        
        for interface in obj.interfaces.accessible_to(user):
            view_names = {
                INTERFACE_TYPES['ethernet']: 'api_ethernet_details',
                INTERFACE_TYPES['wireless']: 'api_wireless_details',
                INTERFACE_TYPES['bridge']: 'api_bridge_details',
                INTERFACE_TYPES['virtual']: 'api_tunnel_details',
                INTERFACE_TYPES['vlan']: 'api_vlan_details'
            }
            link = reverse(view_names[interface.type],
                           args=[interface.id],
                           request=self.context['request'],
                           format=self.context['format'])
            links.append(link)
        
        return links
    
    def validate(self, attrs):
        """ perform many2many validation """
        interfaces = attrs.get('interfaces', [])
        created = False
        
        # redundant but necessary
        if(len(interfaces) < 2 and not self.partial) or \
          (self.partial and 'interfaces' in attrs and len(interfaces) < 2):  # this line adds support for partial udpates with PATCH method
            raise ValidationError(_(u'You must bridge at least 2 interfaces'))
        
        # when creating a new interface self.object is None
        if not self.object:
            created = True
            self.object = Bridge(
                device_id=attrs['device'].id,
                name=attrs['name'],
                mac=attrs['mac']
            )
            self.object.full_clean()
            self.object.save()
        
        # validate many2many
        try:
            validate_bridged_interfaces(
                sender=self.object.interfaces,
                instance=self.object,
                action="pre_add",
                reverse=False,
                model=self.object.interfaces.model,
                pk_set=[interface.id for interface in interfaces]
            )
        except ValidationError as e:
            # delete object first if validation error raised and then raise again
            if created:
                self.object.delete()
            raise ValidationError(e.messages[0])
        
        # delete any created object that was needed for validation only
        if created:
            self.object.delete()
        
        return attrs
    
    class Meta:
        model = Bridge
        fields = InterfaceSerializer.Meta.fields[:] + ['interfaces', 'interfaces_links']
        read_only_fields = ('added', 'updated')


class BridgeDetailSerializer(BridgeSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_bridge_details')
    
    class Meta:
        model = Bridge
        fields = BridgeSerializer.Meta.fields[:] + ['details']
        read_only_fields = ('added', 'updated')


class BridgeAddSerializer(BridgeSerializer):
    class Meta:
        model = Bridge
        fields = BridgeSerializer.Meta.fields[:] + ['device', 'interfaces']
        read_only_fields = ('added', 'updated')


class TunnelSerializer(InterfaceSerializer):
    class Meta:
        model = Tunnel
        fields = InterfaceSerializer.Meta.fields[:] + [
            'sap', 'protocol', 'endpoint',
        ]


class TunnelDetailSerializer(TunnelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_tunnel_details')
    
    class Meta:
        model = Tunnel
        fields = TunnelSerializer.Meta.fields[:] + ['details']
        read_only_fields = ('added', 'updated')


class TunnelAddSerializer(TunnelSerializer):
    class Meta:
        model = Tunnel
        fields = TunnelSerializer.Meta.fields[:] + ['device']
        read_only_fields = ('added', 'updated')


class VlanSerializer(InterfaceSerializer):
    class Meta:
        model = Vlan
        fields = InterfaceSerializer.Meta.fields[:] + ['tag']


class VlanDetailSerializer(VlanSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_vlan_details')
    
    class Meta:
        model = Vlan
        fields = VlanSerializer.Meta.fields[:] + ['details']
        read_only_fields = ('added', 'updated')


class VlanAddSerializer(VlanSerializer):
    class Meta:
        model = Vlan
        fields = VlanSerializer.Meta.fields[:] + ['device']
        read_only_fields = ('added', 'updated')


# ------ IP ADDRESS ------ #


class IpSerializer(serializers.ModelSerializer):
    address = IPAddressField()
    netmask = IPNetworkField()
    
    class Meta:
        model = Ip
        fields = ['address', 'protocol', 'netmask']


class IpAddSerializer(IpSerializer):
    class Meta:
        model = Ip
        fields = IpSerializer.Meta.fields[:] + ['interface']
        read_only_fields = ('added', 'updated')


class IpDetailSerializer(IpSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='api_ip_details')
    
    class Meta:
        model = Ip
        fields = ['id'] + IpSerializer.Meta.fields[:] + ['added', 'updated', 'details']
        read_only_fields = ('added', 'updated')
