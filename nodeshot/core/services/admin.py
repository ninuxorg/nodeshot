from django.contrib import admin
from django.conf import settings
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline#, BaseTabularInline
from models import Category, Service, Login, Url
from nodeshot.core.network.models import Ip

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
    
    #def get_object(self, request, object_id):
    #    """
    #    Hook obj for use in formfield_for_manytomany
    #    """
    #    self.obj = super(UrlInline, self).get_object(request, object_id)
    #    return self.obj
    #
    #def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #    if db_field.name == "ip" and getattr(self, 'obj', False):
    #        kwargs["queryset"] = Ip.objects.select_related().filter(interface__device=self.obj.service.device)
    #        import logging
    #        logging.log(1, 'yo')
    #    return super(UrlInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

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
                '%sgrappelli/tinymce_setup/tinymce_setup.js' % settings.STATIC_URL,
            ]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)