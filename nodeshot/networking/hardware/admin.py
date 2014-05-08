from django.contrib import admin
from django.db import models

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.core.base.widgets import AdvancedFileInput
from nodeshot.networking.net.admin import DeviceAdmin

from models import *


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

class DeviceToModelRelInline(admin.StackedInline):
    model = DeviceToModelRel
    inline_classes = ('grp-collapse grp-open',)
    
    raw_id_fields = ('model',)
    autocomplete_lookup_fields = {
        'fk': ['model'],
    }


class AntennaInline(BaseStackedInline):
    model = Antenna
    extra = 0
    inline_classes = ('grp-collapse grp-open',)
    
    raw_id_fields = ('model',)
    autocomplete_lookup_fields = {
        'fk': ['model'],
    }


DeviceAdmin.inlines.insert(0, DeviceToModelRelInline)
DeviceAdmin.inlines.insert(1, AntennaInline)
