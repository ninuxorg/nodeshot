from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin
from .models import DeviceLogin


class DeviceLoginAdmin(BaseAdmin):
    list_display  = ('__unicode__', 'device', 'node',
                     'host', 'username', 'port', 'puller_class',
                     'added', 'updated')
    list_filter   = ('puller_class', 'added')
    date_hierarchy = 'added'
    ordering = ('-id',)
    search_fields = ('username', 'host')
    
    raw_id_fields = ('node', 'device')
    autocomplete_lookup_fields = {
        'fk': ('node', 'device'),
    }

admin.site.register(DeviceLogin, DeviceLoginAdmin)