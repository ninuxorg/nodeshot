from django.contrib import admin
from nodeshot.core.nodes.models import Node, Zone
from nodeshot.core.network.models import Device
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline

class DeviceInline(BaseStackedInline):
    model = Device

class ZoneAdmin(BaseAdmin):
    pass

class NodeAdmin(BaseAdmin):
    list_display  = ('name', 'user', 'status', 'added', 'updated')
    list_filter   = ('status', 'added')
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (DeviceInline,)

admin.site.register(Zone, ZoneAdmin)
admin.site.register(Node, NodeAdmin)
