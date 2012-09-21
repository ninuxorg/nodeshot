from django.contrib import admin
from django.conf import settings
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline#, BaseTabularInline
from models import ServiceCategory, Service, ServiceLogin, ServicePort

class ServiceCategoryAdmin(BaseAdmin):
    list_display  = ('name', 'description', 'added', 'updated')
    ordering = ('name',)
    search_fields = ('name', 'description')

class PortInline(BaseStackedInline):
    model = ServicePort

class LoginInline(BaseStackedInline):
    model = ServiceLogin

class ServiceAdmin(BaseAdmin):
    list_display  = ('name', 'device', 'category', 'access_level', 'status', 'is_published', 'added', 'updated')
    list_filter   = ('category', 'status', 'is_published')
    filter_horizontal = ['ips']
    search_fields = ('name', 'description', 'uri', 'documentation_url')
    inlines = (PortInline, LoginInline,)

admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service, ServiceAdmin)
