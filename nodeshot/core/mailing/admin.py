from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline#, BaseTabularInline
from nodeshot.core.zones.models import Zone
from models import Inward, Outward

class InwardAdmin(BaseAdmin):
    list_display  = ('from_email', 'from_name', 'to',  'status', 'added', 'updated')
    search_fields = ('from_email', 'from_name')
    #ordering = ('name',)
    #search_fields = ('name', 'description')
    # define the autocomplete_lookup_fields
    if 'grappelli' in settings.INSTALLED_APPS:
        autocomplete_lookup_fields = {
            'generic': [['content_type', 'object_id']],
        }

class OutwardAdmin(BaseAdmin):
    list_display  = ('subject', 'status', 'is_scheduled', 'added', 'updated')
    list_filter   = ('status', 'is_scheduled')
    filter_horizontal = ['zones', 'users']
    search_fields = ('subject',)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'zones':
            kwargs['queryset'] = Zone.objects.filter(is_external=False)
        if db_field.name == 'users':
            kwargs['queryset'] = User.objects.filter(is_active=True)
        return super(OutwardAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    
    if 'grappelli' in settings.INSTALLED_APPS:
        class Media:
            js = [
                '%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
                '%sgrappelli/tinymce_setup/tinymce_setup_ns.js' % settings.STATIC_URL,
            ]

admin.site.register(Inward, InwardAdmin)
admin.site.register(Outward, OutwardAdmin)

