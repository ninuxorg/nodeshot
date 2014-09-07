import os

from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from .models import DeviceConnector


class DeviceConnectorAdmin(BaseAdmin):
    list_display  = (
        'host', 'device', 'node',
        'port', 'backend', 'added', 'updated'
    )
    list_filter   = ('backend', 'added')
    date_hierarchy = 'added'
    ordering = ('-id',)
    search_fields = ('host', 'data')
    
    if 'grappelli' in settings.INSTALLED_APPS:
        raw_id_fields = ('node', 'device')
        autocomplete_lookup_fields = {
            'fk': ('node', 'device'),
        }
        
        change_form_template = 'admin/device_connector_customization.html'

admin.site.register(DeviceConnector, DeviceConnectorAdmin)


# ------ Extend Default Device Admin ------ #


from nodeshot.networking.net.models import Device
from nodeshot.networking.net.admin import DeviceAdmin as BaseDeviceAdmin


class DeviceConnectorInline(BaseStackedInline):
    model = DeviceConnector
    extra = 0
    sortable_field_name = 'order'
    exclude = ['node']


class DeviceAdmin(BaseDeviceAdmin):
    """
    add DeviceConnectorInline to inlines of DeviceAmin
    """
    inlines = BaseDeviceAdmin.inlines + [DeviceConnectorInline]


# unregister BaseDeviceAdmin
admin.site.unregister(Device)
admin.site.register(Device, DeviceAdmin)
