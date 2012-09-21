from django.contrib import admin
from django.conf import settings
from nodeshot.core.links.models import Link, LinkRadio
from nodeshot.core.base.admin import BaseAdmin#, BaseStackedInline, BaseTabularInline

class LinkAdmin(BaseAdmin):
    list_display  = ('interface_a', 'interface_b', 'type', 'status', 'added', 'updated')
    list_filter   = ('status', 'type')
    date_hierarchy = 'added'
    ordering = ('-id',)

admin.site.register(Link, LinkAdmin)
admin.site.register(LinkRadio, LinkAdmin)
