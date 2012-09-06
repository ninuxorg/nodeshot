from django.contrib import admin
from nodeshot.core.nodes.models import Node, Image
from nodeshot.core.network.models import Device
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline, BaseTabularInline

class DeviceInline(BaseStackedInline):
    model = Device

class ImageInline(BaseTabularInline):
    model = Image

class NodeAdmin(BaseAdmin):
    list_display  = ('name', 'user', 'status', 'added', 'updated')
    list_filter   = ('status', 'added')
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (DeviceInline, ImageInline)

admin.site.register(Node, NodeAdmin)
