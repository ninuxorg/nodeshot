from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from nodeshot.core.base.admin import BaseGeoAdmin, PublishActionsAdminMixin

from .settings import REVERSION_ENABLED, TEXT_HTML
from .models import Layer

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
    list_filter = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = []

    # django-grappelli usability improvements
    raw_id_fields = ('mantainers',)
    autocomplete_lookup_fields = {
        'm2m': ['mantainers'],
    }

    if TEXT_HTML:
        # enable editor for "extended text description" only
        html_editor_fields = ['text']

    def view_nodes(self, obj):
        return '<a href="%s?layer__id__exact=%s">%s</a>' % (
            reverse('admin:nodes_node_changelist'),
            obj.pk,
            _('view nodes')
        )
    view_nodes.allow_tags = True

    def publish_action(self, request, queryset):
        super(LayerAdmin, self).publish_action(request, queryset)
        # unpublish all nodes of selected layers
        Layer.node_set.related.model.filter(layer__in=queryset).update(is_published=True)
    publish_action.short_description = _("Publish selected layers (automatically publishes all nodes of layer)")

    def unpublish_action(self, request, queryset):
        super(LayerAdmin, self).unpublish_action(request, queryset)
        # publish all nodes of selected layers
        Layer.node_set.related.model.filter(layer__in=queryset).update(is_published=False)
    unpublish_action.short_description = _("Unpublish selected layers (automatically unpublishes all nodes of layer)")


admin.site.register(Layer, LayerAdmin)
