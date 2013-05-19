from django.contrib import admin
from django.contrib.gis import admin as geoadmin
from django.db import models
from django.conf import settings

from nodeshot.core.nodes.models import Node, Image
from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline, BaseTabularInline
from nodeshot.core.base.widgets import AdvancedFileInput


class ImageInline(BaseStackedInline):
    model = Image
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }
    
    if 'grappelli' in settings.INSTALLED_APPS:
        sortable_field_name = 'order'
        classes = ('grp-collapse grp-open', )


class NodeAdmin(geoadmin.OSMGeoAdmin, BaseAdmin):
    list_display  = ('name', 'status', 'access_level', 'is_published', 'added', 'updated')
    list_filter   = ('status', 'access_level', 'added')
    search_fields = ('name',)
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageInline]
    
    # geodjango
    default_lat = 5145024.63201869
    default_lon = 1391048.3569527462
    default_zoom = '3'
    
    change_list_template = 'smuggler/change_list.html'


admin.site.register(Node, NodeAdmin)
