from django.contrib import admin

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.core.layers.admin import Layer, LayerAdmin as BaseLayerAdmin

from models import LayerExternal
import os


class LayerExternalInline(admin.StackedInline):
    model = LayerExternal
    fk_name = 'layer'


class LayerAdmin(BaseLayerAdmin):
    list_display = ('name', 'is_published', 'description', 'organization', 'email', 'is_external', 'added', 'updated')
    list_filter   = ('is_external', 'is_published')
    search_fields = ('name', 'description', 'organization', 'email')
    filter_horizontal = ('mantainers',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [LayerExternalInline]
    # custom admin template
    change_form_template = '%s/templates/admin/layer_change_form.html' % os.path.dirname(os.path.realpath(__file__))


admin.site.unregister(BaseLayerAdmin)
admin.site.register(Layer, LayerAdmin)