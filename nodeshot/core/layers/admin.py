from django.contrib import admin

from nodeshot.core.base.admin import BaseAdmin
from models import Layer


class LayerAdmin(BaseAdmin):
    list_display = ('name', 'is_published', 'description', 'organization', 'email', 'is_external', 'added', 'updated')
    list_filter   = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Layer, LayerAdmin)