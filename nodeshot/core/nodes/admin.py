from django.contrib import admin
from nodeshot.core import nodes
from nodeshot.core.base.admin import BaseAdmin

class ZoneAdmin(BaseAdmin):
    pass

class NodeAdmin(BaseAdmin):
    pass

admin.site.register(nodes.models.Zone, ZoneAdmin)
admin.site.register(nodes.models.Node, NodeAdmin)
