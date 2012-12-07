from django.contrib import admin
from django.conf import settings
from django.db import models
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.dependencies.widgets import AdvancedFileInput
from models import Manufacturer, MacPrefix, DeviceModel, Device2Model

class MacPrefixInline(admin.StackedInline):
    model = MacPrefix
    extra = 0
    inline_classes = ('grp-collapse grp-open',)

class ManufacturerAdmin(BaseAdmin):
    list_display  = ('name', 'logo_img_tag', 'url_tag', 'added', 'updated')
    list_display_links = ('name', 'logo_img_tag')
    search_fields = ('name',)
    inlines = [MacPrefixInline]
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }

class DeviceModelAdmin(BaseAdmin):
    list_display  = ('name', 'image_img_tag', 'added', 'updated')
    list_display_links = ('name', 'image_img_tag')
    search_fields = ('name',)
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }

admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(DeviceModel, DeviceModelAdmin)

from nodeshot.core.network.models import Device
from nodeshot.core.network.admin import DeviceAdmin

class Device2ModelInline(admin.StackedInline):
    model = Device2Model
    inline_classes = ('grp-collapse grp-open',)

class ExtendedDeviceAdmin(DeviceAdmin):
    inlines = DeviceAdmin.inlines.insert(0, Device2ModelInline)

admin.site.unregister(Device)
admin.site.register(Device, DeviceAdmin)