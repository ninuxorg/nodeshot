from django.contrib import admin
from django.db import models

from nodeshot.core.base.admin import BaseGeoAdmin, BaseStackedInline, PublishActionsAdminMixin
from nodeshot.core.base.widgets import AdvancedFileInput

from .settings import settings, REVERSION_ENABLED, DESCRIPTION_HTML
from .models import Node, Status, Image


# enable django-reversion according to settings
if REVERSION_ENABLED:
    import reversion

    class GeoAdmin(BaseGeoAdmin, reversion.VersionAdmin):
        change_list_template = 'reversion_and_smuggler/change_list.html'
else:
    class GeoAdmin(BaseGeoAdmin):
        change_list_template = 'smuggler/change_list.html'


class ImageInline(BaseStackedInline):
    model = Image

    formfield_overrides = {
        models.ImageField: {'widget': AdvancedFileInput(image_width=250)},
    }

    if 'grappelli' in settings.INSTALLED_APPS:
        sortable_field_name = 'order'
        classes = ('grp-collapse grp-open', )


NODE_FILTERS = ['is_published', 'status', 'access_level', 'added', 'updated']
NODE_LIST_DISPLAY = ['name', 'user', 'status', 'access_level', 'is_published', 'added', 'updated']
NODE_FIELDS_LOOKEDUP = [
    'user__id', 'user__username',
    'status__id', 'status__name', 'status__is_default',
    'name', 'access_level', 'is_published', 'added', 'updated'
]

# include layer in filters if layers app installed
if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    NODE_FILTERS.insert(0, 'layer')
    NODE_LIST_DISPLAY.insert(2, 'layer')
    NODE_FIELDS_LOOKEDUP += ['layer__id', 'layer__name']


class NodeAdmin(PublishActionsAdminMixin, GeoAdmin):
    list_display = NODE_LIST_DISPLAY
    list_filter = NODE_FILTERS
    list_select_related = True
    search_fields = ('name',)
    actions_on_bottom = True
    date_hierarchy = 'added'
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageInline]

    # django-grappelli usability improvements
    raw_id_fields = ('layer', 'user')
    autocomplete_lookup_fields = {
        'fk': ('layer', 'user'),
    }

    def queryset(self, request):
        return super(NodeAdmin, self).queryset(request).select_related('user', 'layer', 'status')

    if DESCRIPTION_HTML:
        # enable editor for "node description" only
        html_editor_fields = ['description']


class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'order', 'is_default')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', )

    change_list_template = 'smuggler/change_list.html'


admin.site.register(Node, NodeAdmin)
admin.site.register(Status, StatusAdmin)
