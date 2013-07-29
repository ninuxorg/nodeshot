from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.networking.net.models import Ip

from .models import Category, Service, Login, Url


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


class LoginInline(BaseStackedInline):
    model = Login


class ServiceAdmin(BaseAdmin):
    list_display  = ('name', 'device', 'category', 'access_level', 'status', 'is_published', 'added', 'updated')
    list_filter   = ('category', 'status', 'is_published')
    search_fields = ('name', 'description', 'documentation_url')
    inlines = (UrlInline, LoginInline,)

    if 'grappelli' in settings.INSTALLED_APPS:
        class Media:
            js = [
                '%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
                '%sgrappelli/tinymce_setup/tinymce_setup_ns.js' % settings.STATIC_URL,
            ]
        
        # enable editor for "node description" only
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(ServiceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            
            if db_field.name == 'description':
                field.widget.attrs['class'] = 'html-editor %s' % field.widget.attrs.get('class', '')
            
            return field

admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)