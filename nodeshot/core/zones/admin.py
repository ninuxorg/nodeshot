from django.contrib import admin
from nodeshot.core.base.admin import BaseAdmin
from models import Zone, ZoneExternal

class ZoneAdmin(BaseAdmin):
    list_display = ('name', 'description', 'is_external')

admin.site.register(Zone, ZoneAdmin)
admin.site.register(ZoneExternal, ZoneAdmin)