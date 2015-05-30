from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseGeoAdmin, BaseStackedInline

from .models.choices import INTERFACE_TYPES
from .models import *


class DeviceInline(BaseStackedInline):
    model = Device
    
    if not settings.DEBUG:
        readonly_fields =  [
            'status', 'first_seen', 'last_seen'
        ] + BaseStackedInline.readonly_fields
    
    if 'grappelli' in settings.INSTALLED_APPS:
        classes = ('grp-collapse grp-open', )
        
        raw_id_fields = ('routing_protocols',)
        autocomplete_lookup_fields = {
            'm2m': ['routing_protocols']
        }


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


class DeviceAdmin(BaseGeoAdmin):
    list_filter   = ('added', 'updated',)
    list_display  = ('name', 'status', 'node', 'type', 'access_level', 'added', 'updated')
    search_fields = ('name', 'type')
    inlines = [EthernetInline, WirelessInline, BridgeInline, TunnelInline, VlanInline]
    
    raw_id_fields = ('node', 'routing_protocols')
    autocomplete_lookup_fields = {
        'fk': ['node'],
        'm2m': ['routing_protocols']
    }
    
    exclude = ('shortcuts',)
    
    if not settings.DEBUG:
        readonly_fields =  [
            'status', 'first_seen', 'last_seen'
        ] + BaseAdmin.readonly_fields


class InterfaceAdmin(BaseAdmin):
    list_display  = ('mac', 'name', 'type', 'device', 'added', 'updated')
    search_fields = ('mac',)
    exclude = ('shortcuts',)
    inlines = (IpInline,)
    
    raw_id_fields = ('device',)
    autocomplete_lookup_fields = {
        'fk': ['device'],
    }


class WirelessAdmin(InterfaceAdmin):
    inlines = (IpInline, VapInline)   


class RoutingProtocolAdmin(BaseAdmin):
    list_display   = ('name', 'version')


class IpAdmin(BaseAdmin):
    list_display = ('address', 'netmask', 'protocol', 'added', 'updated')
    list_filter = ('protocol', 'added', 'updated')
    search_fields = ('address',)
    
    raw_id_fields = ('interface',)
    autocomplete_lookup_fields = {
        'fk': ['interface'],
    }
    
    readonly_fields = ['protocol'] + BaseAdmin.readonly_fields


from django import forms
from .models.interfaces.bridge import validate_bridged_interfaces

class BridgeForm(forms.ModelForm):
    class Meta:
        model = Bridge
    
    def __init__(self, *args, **kwargs):
        """ only interfaces of the same device can be bridged """
        super(BridgeForm, self).__init__(*args, **kwargs)
        self.fields['interfaces'].queryset = Interface.objects.filter(device_id=self.instance.device_id) \
                                             .exclude(type=INTERFACE_TYPES.get('bridge'))
    
    def clean_interfaces(self):
        """ interface many2many validation """
        interfaces = self.cleaned_data.get('interfaces', [])
        if interfaces:
            # custom signal
            validate_bridged_interfaces(
                sender=self.instance.interfaces,
                instance=self.instance,
                action="pre_add",
                reverse=False,
                model=self.instance.interfaces.model,
                pk_set=interfaces
            )
        return self.cleaned_data['interfaces']


class BridgeAdmin(InterfaceAdmin):
    form = BridgeForm 


admin.site.register(Device, DeviceAdmin)
admin.site.register(Interface, InterfaceAdmin)

admin.site.register(Ethernet, InterfaceAdmin)
admin.site.register(Wireless, WirelessAdmin)
admin.site.register(Bridge, BridgeAdmin)
admin.site.register(Tunnel, InterfaceAdmin)
admin.site.register(Vlan, InterfaceAdmin)

admin.site.register(RoutingProtocol, RoutingProtocolAdmin)
admin.site.register(Ip, IpAdmin)


# ------ Add Device Inlines to NodeAdmin ------ #

from nodeshot.core.nodes.admin import NodeAdmin

NodeAdmin.inlines = [DeviceInline] + NodeAdmin.inlines
