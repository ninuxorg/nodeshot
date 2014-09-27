from django.contrib import admin
from django.contrib.gis import forms
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.admin import ModelAdmin as GeoModelAdmin

# TODO these settings at the moment are not being used
from .settings import ADMIN_MAP_COORDINATES, ADMIN_MAP_ZOOM


def _get_geodjango_map_coords():
    """ point to be used by geodjango """
    try:
        lat, lng = ADMIN_MAP_COORDINATES
    except KeyError:
        raise ImproperlyConfigured("incorrect NODESHOT_ADMIN_MAP_COORDINATES setting")
    return lat, lng


def _get_geodjango_map_zoom():
    """ zoom level to be used by geodjango """
    try:
        return ADMIN_MAP_ZOOM
    except KeyError:
        raise ImproperlyConfigured("incorrect NODESHOT_ADMIN_MAP_ZOOM setting")


class BaseAdmin(admin.ModelAdmin):
    """
    Abstract administration model for BaseDate models.
        * 'added' and 'updated' fields readonly
        * save-on-top button enabled by default
    """
    save_on_top = True
    readonly_fields = ['added', 'updated']
    html_editor_fields = []
    # preload tinymce editor static files
    if 'grappelli' in settings.INSTALLED_APPS:
        class Media:
            js = [
                '%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
                '%sgrappelli/tinymce_setup/tinymce_setup_ns.js' % settings.STATIC_URL,
            ]
        # enable editor for "node description" only
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(BaseAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            if db_field.name in self.html_editor_fields:
                field.widget.attrs['class'] = 'html-editor %s' % field.widget.attrs.get('class', '')
            return field


class GeoForm(forms.ModelForm):
    # TODO entirely configurable
    geometry = forms.GeometryField(widget=forms.OSMWidget(attrs={
        'map_width': 758,
        'map_height': 500,
        'display_raw': settings.DEBUG
    }))


class BaseGeoAdmin(BaseAdmin, GeoModelAdmin):
    """
    BaseAdmin + Geodjango support
    """
    form = GeoForm


class PublishActionsAdminMixin(object):
    """
    Admin mixin that adds 2 actions in the admin list:
        * publish objects
        * unpublish objects
    """
    actions = ['publish_action', 'unpublish_action']

    def publish_action(self, request, queryset):
        rows_updated = queryset.update(is_published=True)

        if rows_updated == 1:
            message_bit = _("1 item was")
        else:
            message_bit = _("%s items were") % rows_updated

        self.message_user(request, _("%s successfully published.") % message_bit)

    publish_action.short_description = _("Publish selected items")

    def unpublish_action(self, request, queryset):
        rows_updated = queryset.update(is_published=False)

        if rows_updated == 1:
            message_bit = _("1 item was")
        else:
            message_bit = _("%s items were") % rows_updated

        self.message_user(request, _("%s successfully unpublished.") % message_bit)

    unpublish_action.short_description = _("Unpublish selected items")


class BaseStackedInline(admin.StackedInline):
    readonly_fields = ['added', 'updated']
    extra = 0


class BaseTabularInline(admin.TabularInline):
    readonly_fields = ['added', 'updated']
    extra = 0
