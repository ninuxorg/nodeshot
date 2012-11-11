import os
from django.contrib import admin
from django.conf import settings
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from models import Zone, ZonePoint, ZoneExternal


class ZonePointInline(admin.StackedInline):
    model = ZonePoint
    extra = 0
    
    if 'grappelli' in settings.INSTALLED_APPS:
        classes = ('grp-collapse grp-open', )

class ZoneExternalInline(admin.StackedInline):
    model = ZoneExternal
    fk_name = 'zone'

class ZoneAdmin(BaseAdmin):
    list_display = ('name', 'is_published', 'description', 'organization', 'email', 'is_external', 'added', 'updated')
    list_filter   = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ZonePointInline, ZoneExternalInline]
    # custom admin template
    change_form_template = '%s/templates/admin/zone_change_form.html' % os.path.dirname(os.path.realpath(__file__))


admin.site.register(Zone, ZoneAdmin)
#admin.site.register(ZoneExternal, ZoneAdmin)