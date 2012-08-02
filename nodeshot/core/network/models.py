from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate, BaseAccessLevel
from nodeshot.core.nodes.models import Node
from nodeshot.core.base.choices import ROUTING_PROTOCOLS, DEVICE_STATUS, DEVICE_TYPES, INTERFACE_TYPE, IP_PROTOCOLS, ETHERNET_STANDARDS, WIRELESS_STANDARDS, DUPLEX_CHOICES

class RoutingProtocol(BaseDate):
    name = models.CharField(_('name'), max_length=50, choices=ROUTING_PROTOCOLS)
    version = models.CharField(_('version'), max_length=10)
    url = models.URLField(_('url'))
    
    class Meta:
        db_table = 'network_routing_protocol'

class Device(BaseAccessLevel):
    name = models.CharField(_('name'), max_length=50)
    node = models.ForeignKey(Node, verbose_name=_('node'))
    type = models.CharField(_('type'), max_length=50, choices=DEVICE_TYPES)
    routing_protocols = models.ManyToManyField(RoutingProtocol, blank=True)
    status = models.CharField(_('status'), max_length=1, choices=DEVICE_STATUS, default=DEVICE_STATUS[1][0])
    firmware = models.CharField(_('firmware'), max_length=20, blank=True, null=True)
    os = models.CharField(_('operating system'), max_length=20, blank=True, null=True)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    #notes = models.TextField(_('notes'), blank=True, null=True)

class Interface(BaseAccessLevel):
    device = models.ForeignKey(Device)
    type = models.CharField(_('type'), max_length=10, choices=INTERFACE_TYPE)
    name = models.CharField(_('name'), max_length=10, blank=True, null=True)
    mac = models.CharField(_('mac_address'), max_length=17, unique=True, default=None)
    mtu = models.IntegerField(_('MTU (Maximum Trasmission Unit)'), blank=True, null=True)
    tx_rate = models.IntegerField(_('TX Rate'), null=True, default=None)
    rx_rate = models.IntegerField(_('RX Rate'), null=True, default=None)

class Ip(BaseAccessLevel):
    interface = models.ForeignKey(Interface, verbose_name=_('interface'))
    address = models.GenericIPAddressField(verbose_name=_('ip address'), unique=True)
    protocol = models.CharField(_('IP Protocol Version'), max_length=4, choices=IP_PROTOCOLS, default=IP_PROTOCOLS[0][0])
    netmask = models.CharField(_('netmask'), max_length=100)

class Ethernet(Interface):
    standard = models.CharField(_('type'), max_length=15, choices=ETHERNET_STANDARDS)
    duplex = models.CharField(_('type'), max_length=15, choices=DUPLEX_CHOICES)
    
    class Meta:
        db_table = 'network_interface_ethernet'

class Wireless(Interface):
    wireless_mode = models.CharField(max_length=5)
    wireless_standard = models.CharField(max_length=7, choices=WIRELESS_STANDARDS)
    wireless_channel = models.CharField(max_length=4, blank=True, null=True)
    channel_width = models.CharField(max_length=6, blank=True, null=True)
    transmitpower = models.IntegerField(null=True, blank=True)
    dbm = models.IntegerField(_('dBm'), null=True, default=None)
    noise = models.IntegerField(_('noise'), null=True, default=None)
    
    class Meta:
        db_table = 'network_interface_wireless'

class Bridge(Interface):
    interfaces = models.ManyToManyField(Interface, verbose_name=_('interfaces'), related_name='bridge_interfaces')
    
    class Meta:
        db_table = 'network_interface_bridge'

class Tunnel(Interface):
    sap = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=10) # GRE, ... ecc
    endpoint = models.ForeignKey('Ip', verbose_name=_('ip address'))
    
    class Meta:
        db_table = 'network_interface_tunnel'

class Vlan(Interface):
    tag = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'network_interface_vlan'
    
class Vap(BaseDate):
    interface = models.ForeignKey(Wireless, verbose_name='wireless interface')
    essid = models.CharField(max_length=50)
    bssid = models.CharField(max_length=50, null=True, blank=True)
    encryption = models.CharField(max_length=50, null=True, blank=True)
    key = models.CharField(max_length=100, null=True, blank=True)
    auth_server = models.CharField(max_length=50, null=True, blank=True)
    auth_port = models.IntegerField(null=True, blank=True)
    accounting_server = models.CharField(max_length=50, null=True, blank=True)
    accounting_port = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'network_interface_vap'