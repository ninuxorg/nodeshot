from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _

from nodeshot.core.base.admin import BaseGeoAdmin
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


class LayerAdmin(GeoAdmin):
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
    
    def view_nodes(self, obj):
        return '<a href="%s?layer__id__exact=%s">%s</a>' % (
            reverse('admin:nodes_node_changelist'),
            obj.pk,
            _('view nodes')
        )
    view_nodes.allow_tags = True
    
    # Enable TinyMCE HTML Editor according to settings, defaults to True
    if settings.NODESHOT['SETTINGS'].get('LAYER_TEXT_HTML', True) is True: 
        if 'grappelli' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured(
                _("settings.NODESHOT['SETTINGS']['LAYER_TEXT_HTML'] is set to\
                  True but grappelli is not in settings.INSTALLED_APPS")
            )
        
        class Media:
            js = [
                '%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js' % settings.STATIC_URL,
                '%sgrappelli/tinymce_setup/tinymce_setup_ns.js' % settings.STATIC_URL,
            ]
        
        # enable editor for "extended text description" only
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(LayerAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            
            if db_field.name == 'text':
                _class = 'html-editor %s' % field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = _class
            
            return field


admin.site.register(Layer, LayerAdmin)