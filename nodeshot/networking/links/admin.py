from django.contrib import admin

from nodeshot.core.base.admin import BaseGeoAdmin
from .models import Link


class LinkAdmin(BaseGeoAdmin):
    list_display = (
        '__unicode__',
        'type',
        'status',
        'interface_a_mac',
        'interface_b_mac',
        'added',
        'updated'
    )
    list_filter = ('status', 'type')
    date_hierarchy = 'added'
    ordering = ('-id',)

    raw_id_fields = ('interface_a', 'interface_b', 'node_a', 'node_b')
    autocomplete_lookup_fields = {
        'fk': ['interface_a', 'interface_b', 'node_a', 'node_b'],
    }

    readonly_fields = [
        'first_seen', 'last_seen',
        'metric_value', 'min_rate', 'max_rate',
        'dbm', 'noise'
    ] + BaseGeoAdmin.readonly_fields[:]
    exclude = ('shortcuts',)


admin.site.register(Link, LinkAdmin)
