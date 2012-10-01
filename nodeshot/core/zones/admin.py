from django.contrib import admin
from django.conf import settings
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from models import Zone, ZonePoint, ZoneExternal

class ZonePointInline(admin.StackedInline):
    model = ZonePoint
    extra = 0
    
    if 'grappelli' in settings.INSTALLED_APPS:
        classes = ('grp-collapse grp-open', )

class ZoneAdmin(BaseAdmin):
    list_display = ('name', 'description', 'is_external', 'mantainers', 'email', 'time_zone')
    prepopulated_fields = {'slug': ('name',)}
    list_filter   = ('is_external',)
    inlines = [ZonePointInline]

admin.site.register(Zone, ZoneAdmin)
#admin.site.register(ZoneExternal, ZoneAdmin)