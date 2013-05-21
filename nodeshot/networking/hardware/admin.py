from django.contrib import admin
from django.conf import settings
from django.db import models

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.core.base.widgets import AdvancedFileInput

from models import Manufacturer, MacPrefix, DeviceModel, DeviceToModelRel, AntennaModel, Antenna, RadiationPattern


class MacPrefixInline(admin.StackedInline):
    model = MacPrefix
    extra = 0
    inline_classes = ('grp-collapse grp-open',)


class ManufacturerAdmin(BaseAdmin):
    list_display  = ('name', 'image_img_tag', 'url_tag', 'added', 'updated')
    list_display_links = ('name', 'image_img_tag')
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


class RadiationPatternInline(BaseStackedInline):
    model = RadiationPattern
    extra = 0
    inline_classes = ('grp-collapse grp-open',)


class AntennaModelAdmin(BaseAdmin):
    list_display  = ('name', 'image_img_tag', 'added', 'updated')
    list_display_links = ('name', 'image_img_tag')
    search_fields = ('name',)
    inlines = [RadiationPatternInline]
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }


admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(DeviceModel, DeviceModelAdmin)
admin.site.register(AntennaModel, AntennaModelAdmin)

# Extend Default Device Admin

from nodeshot.networking.net.models import Device
from nodeshot.networking.net.admin import DeviceAdmin


class DeviceToModelRelInline(admin.StackedInline):
    model = DeviceToModelRel
    inline_classes = ('grp-collapse grp-open',)


class AntennaInline(BaseStackedInline):
    model = Antenna
    extra = 0
    inline_classes = ('grp-collapse grp-open',)


class ExtendedDeviceAdmin(DeviceAdmin):
    DeviceAdmin.inlines.insert(0, DeviceToModelRelInline)
    DeviceAdmin.inlines.insert(1, AntennaInline)


admin.site.unregister(Device)
admin.site.register(Device, DeviceAdmin)