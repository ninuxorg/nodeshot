from django.contrib.gis import admin

from nodeshot.core.base.admin import BaseGeoAdmin
from models import Layer


class LayerAdmin(BaseGeoAdmin):
    list_display = ('name', 'is_published', 'organization', 'email', 'is_external', 'new_nodes_allowed', 'added', 'updated')
    list_filter   = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Layer, LayerAdmin)