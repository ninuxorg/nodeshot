from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin
from .models import Link


class LinkAdmin(BaseAdmin):
    list_display  = ('interface_a', 'interface_b', 'type', 'status', 'added', 'updated')
    list_filter   = ('status', 'type')
    date_hierarchy = 'added'
    ordering = ('-id',)


admin.site.register(Link, LinkAdmin)