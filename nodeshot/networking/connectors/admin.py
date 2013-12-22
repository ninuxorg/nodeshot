import os

from django.contrib import admin
from django.conf import settings
from django.forms import ModelForm, CharField, PasswordInput

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from .models import DeviceConnector


class DeviceConnectorForm(ModelForm):
    password = CharField(widget=PasswordInput(render_value=True), required=False)
    
    class Meta:
        model = DeviceConnector


class DeviceConnectorAdmin(BaseAdmin):
    list_display  = ('__unicode__', 'device', 'node',
                     'host', 'username', 'port', 'connector_class',
                     'added', 'updated')
    list_filter   = ('connector_class', 'added')
    date_hierarchy = 'added'
    ordering = ('-id',)
    search_fields = ('username', 'host')
    
    form = DeviceConnectorForm
    
    raw_id_fields = ('node', 'device')
    autocomplete_lookup_fields = {
        'fk': ('node', 'device'),
    }
    
    change_form_template = '%s/templates/admin/device_connector_customization.html' % os.path.dirname(os.path.realpath(__file__))

admin.site.register(DeviceConnector, DeviceConnectorAdmin)


# ------ Extend Default Device Admin ------ #


from nodeshot.networking.net.models import Device
from nodeshot.networking.net.admin import DeviceAdmin as BaseDeviceAdmin


class DeviceConnectorInline(BaseStackedInline):
    model = DeviceConnector
    form = DeviceConnectorForm
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