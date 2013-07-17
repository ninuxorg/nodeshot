from django.contrib import admin
from django.db import models
from django.conf import settings

from nodeshot.core.nodes.models import Node, Image
from nodeshot.core.base.admin import BaseGeoAdmin, BaseStackedInline
from nodeshot.core.base.widgets import AdvancedFileInput


class ImageInline(BaseStackedInline):
    model = Image
    
    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }
    
    if 'grappelli' in settings.INSTALLED_APPS:
        sortable_field_name = 'order'
        classes = ('grp-collapse grp-open', )


NODE_FILTERS = ['is_published', 'status', 'access_level', 'added']

# include layer in filters if layers app installed
if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    NODE_FILTERS = ['layer'] + NODE_FILTERS


class NodeAdmin(BaseGeoAdmin):
    list_display  = ('name', 'status', 'access_level', 'is_published', 'added', 'updated')
    list_filter   = NODE_FILTERS
    search_fields = ('name',)
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageInline]
    
    change_list_template = 'smuggler/change_list.html'


admin.site.register(Node, NodeAdmin)
