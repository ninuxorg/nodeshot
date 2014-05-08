from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _

from nodeshot.core.base.admin import BaseGeoAdmin, PublishActionsAdminMixin
from models import Layer

REVERSION_ENABLED = settings.NODESHOT['SETTINGS'].get('REVERSION_LAYERS', True)

# enable django-reversion according to settings
if REVERSION_ENABLED:
    import reversion
    
    class GeoAdmin(BaseGeoAdmin, reversion.VersionAdmin):
        change_list_template = 'reversion_and_smuggler/change_list.html'
else:
    class GeoAdmin(BaseGeoAdmin):
        change_list_template = 'smuggler/change_list.html'


class LayerAdmin(PublishActionsAdminMixin, GeoAdmin):
    list_display = (
        'name', 'is_published', 'view_nodes',
        'organization', 'email', 'is_external',
        'new_nodes_allowed', 'added', 'updated'
    )
    list_filter   = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = []
    
    # django-grappelli usability improvements
    raw_id_fields = ('mantainers',)
    autocomplete_lookup_fields = {
        'm2m': ['mantainers'],
    }
    
    if settings.NODESHOT['SETTINGS'].get('LAYER_TEXT_HTML', True) is True:  
        # enable editor for "extended text description" only
        html_editor_fields = ['text']
    
    def view_nodes(self, obj):
        return '<a href="%s?layer__id__exact=%s">%s</a>' % (
            reverse('admin:nodes_node_changelist'),
            obj.pk,
            _('view nodes')
        )
    view_nodes.allow_tags = True


admin.site.register(Layer, LayerAdmin)
