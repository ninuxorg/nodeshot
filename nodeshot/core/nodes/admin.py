from django.contrib import admin
from django.db import models
from django.conf import settings
from nodeshot.core.nodes.models import Node, Image
from nodeshot.core.network.models import Device
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline, BaseTabularInline
from nodeshot.dependencies.widgets import AdvancedFileInput


class DeviceInline(BaseStackedInline):
    model = Device
    
    if 'grappelli' in settings.INSTALLED_APPS:
        classes = ('grp-collapse grp-open', )


class ImageInline(BaseStackedInline):
    model = Image
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }
    
    if 'grappelli' in settings.INSTALLED_APPS:
        sortable_field_name = 'order'
        classes = ('grp-collapse grp-open', )


class NodeAdmin(BaseAdmin):
    list_display  = ('name', 'user', 'status', 'access_level', 'is_hotspot', 'added', 'updated')
    list_filter   = ('status', 'is_hotspot', 'access_level', 'added')
    search_fields = ('name',)
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (DeviceInline, ImageInline)
    

admin.site.register(Node, NodeAdmin)
