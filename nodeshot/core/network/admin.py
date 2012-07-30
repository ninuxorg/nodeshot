from django.contrib import admin
from nodeshot.core import network
from nodeshot.core.base.admin import BaseAdmin

class DeviceAdmin(BaseAdmin):
    pass

class InterfaceAdmin(BaseAdmin):
    pass

admin.site.register(network.models.Device, DeviceAdmin)
admin.site.register(network.models.Interface, InterfaceAdmin)

