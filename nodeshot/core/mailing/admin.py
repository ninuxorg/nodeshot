from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline#, BaseTabularInline
from models import Inward, Outward

class InwardAdmin(BaseAdmin):
    list_display  = ('from_email', 'from_name', 'to',  'status', 'added', 'updated')
    #ordering = ('name',)
    #search_fields = ('name', 'description')
    # define the autocomplete_lookup_fields
    if 'grappelli' in settings.INSTALLED_APPS:
        autocomplete_lookup_fields = {
            'generic': [['content_type', 'object_id']],
        }

class OutwardAdmin(BaseAdmin):
    #list_display  = ('name', 'device', 'category', 'access_level', 'status', 'is_published', 'added', 'updated')
    #list_filter   = ('category', 'status', 'is_published')
    #filter_horizontal = ['ips']
    #search_fields = ('name', 'description', 'uri', 'documentation_url')
    #inlines = (PortInline, LoginInline,)
    
    #def get_object(self, request, object_id):
    #    """
    #    Hook obj for use in formfield_for_manytomany
    #    """
    #    self.obj = super(ServiceAdmin, self).get_object(request, object_id)
    #    return self.obj
    #
    #def formfield_for_manytomany(self, db_field, request, **kwargs):
    #    if db_field.name == "ips" and getattr(self, 'obj', None):
    #        kwargs["queryset"] = Ip.objects.select_related().filter(interface__device=self.obj.device)
    #    return super(ServiceAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    pass

admin.site.register(Inward, InwardAdmin)
admin.site.register(Outward, OutwardAdmin)

