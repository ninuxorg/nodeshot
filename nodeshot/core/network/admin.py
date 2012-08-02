from django.contrib import admin
from nodeshot.core.network.models import Device, Interface, Ethernet, Wireless, Bridge, Tunnel, Vap, Vlan, RoutingProtocol, Ip
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline

class InterfaceInline(BaseStackedInline):
    model = Interface

class IpInline(BaseStackedInline):
    model = Ip
    
class VapInline(BaseStackedInline):
    model = Vap

class DeviceAdmin(BaseAdmin):
    list_filter   = ('added', 'updated', 'node')
    list_display  = ('name', 'node', 'type', 'added', 'updated')
    search_fields = ('name', 'type')
    inlines = (InterfaceInline,)

class InterfaceAdmin(BaseAdmin):
    list_display  = ('mac', 'name', 'type', 'device', 'added', 'updated')
    search_fields = ('mac',)
    inlines = (IpInline,)    

class WirelessAdmin(InterfaceAdmin):
    inlines = (IpInline,VapInline)   

class RoutingProtocolAdmin(BaseAdmin):
    pass

class IpAdmin(BaseAdmin):
    pass

admin.site.register(Device, DeviceAdmin)
#admin.site.register(Interface, InterfaceAdmin)

admin.site.register(Ethernet, InterfaceAdmin)
admin.site.register(Wireless, WirelessAdmin)
admin.site.register(Bridge, InterfaceAdmin)
admin.site.register(Tunnel, InterfaceAdmin)
admin.site.register(Vlan, InterfaceAdmin)

admin.site.register(RoutingProtocol, RoutingProtocolAdmin)
admin.site.register(Ip, IpAdmin)

