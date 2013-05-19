from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.core.nodes.models import Node

from .models import Device, Interface, Ethernet, Wireless, Bridge, Tunnel, Vap, Vlan, RoutingProtocol, Ip

if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
    from nodeshot.community.participation.admin import NodeAdmin as BaseNodeAdmin
else:
    from nodeshot.core.nodes.admin import NodeAdmin as BaseNodeAdmin


class DeviceInline(BaseStackedInline):
    model = Device
    
    if 'grappelli' in settings.INSTALLED_APPS:
        classes = ('grp-collapse grp-open', )


class NodeAdmin(BaseNodeAdmin):
    inlines = [DeviceInline] + BaseNodeAdmin.inlines


class EthernetInline(BaseStackedInline):
    model = Ethernet


class WirelessInline(BaseStackedInline):
    model = Wireless


class BridgeInline(BaseStackedInline):
    model = Bridge


class TunnelInline(BaseStackedInline):
    model = Tunnel


class VlanInline(BaseStackedInline):
    model = Vlan


class IpInline(BaseStackedInline):
    model = Ip


class VapInline(BaseStackedInline):
    model = Vap


class DeviceAdmin(BaseAdmin):
    list_filter   = ('added', 'updated', 'node')
    list_display  = ('name', 'node', 'type', 'access_level', 'added', 'updated')
    search_fields = ('name', 'type')
    inlines = [EthernetInline, WirelessInline, BridgeInline, TunnelInline, VlanInline]
    
    if not settings.DEBUG:
        readonly_fields = BaseAdmin.readonly_fields + ['status']


class InterfaceAdmin(BaseAdmin):
    list_display  = ('mac', 'name', 'type', 'device', 'added', 'updated')
    search_fields = ('mac',)
    inlines = (IpInline,)    


class WirelessAdmin(InterfaceAdmin):
    inlines = (IpInline,VapInline)   


class RoutingProtocolAdmin(BaseAdmin):
    list_display   = ('name', 'version', 'url')


class IpAdmin(BaseAdmin):
    list_display = ('address', 'netmask', 'protocol', 'added', 'updated')
    list_filter = ('protocol', 'added', 'updated')
    search_fields = ('address',)
    
    readonly_fields = ['protocol'] + BaseAdmin.readonly_fields


admin.site.unregister(Node)
admin.site.register(Node, NodeAdmin)

admin.site.register(Device, DeviceAdmin)
#admin.site.register(Interface, InterfaceAdmin)

admin.site.register(Ethernet, InterfaceAdmin)
admin.site.register(Wireless, WirelessAdmin)
admin.site.register(Bridge, InterfaceAdmin)
admin.site.register(Tunnel, InterfaceAdmin)
admin.site.register(Vlan, InterfaceAdmin)

admin.site.register(RoutingProtocol, RoutingProtocolAdmin)
admin.site.register(Ip, IpAdmin)

