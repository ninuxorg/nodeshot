from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline

from .models import Category, Service, ServiceLogin, Url


class CategoryAdmin(BaseAdmin):
    list_display  = ('name', 'description', 'added', 'updated')
    ordering = ('name',)
    search_fields = ('name', 'description')


class UrlInline(BaseStackedInline):
    model = Url
    
    if 'grappelli' in settings.INSTALLED_APPS:
        # define the raw_id_fields
        raw_id_fields = ('ip',)
        # define the autocomplete_lookup_fields
        autocomplete_lookup_fields = {
            'fk': ['ip'],
        }


class ServiceLoginInline(BaseStackedInline):
    model = ServiceLogin


class ServiceAdmin(BaseAdmin):
    list_display  = ('name', 'device', 'category', 'access_level', 'status', 'is_published', 'added', 'updated')
    list_filter   = ('category', 'status', 'is_published')
    search_fields = ('name', 'description', 'documentation_url')
    inlines = (UrlInline, ServiceLoginInline,)

    raw_id_fields = ('device',)
    autocomplete_lookup_fields = {
        'fk': ('device',),
    }
    
    # enable editor for "description" only
    html_editor_fields = ['description']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)
