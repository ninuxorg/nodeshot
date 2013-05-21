from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.core.layers.admin import Layer, LayerAdmin as BaseLayerAdmin

from models import LayerExternal
import os


class LayerExternalInline(admin.StackedInline):
    model = LayerExternal
    fk_name = 'layer'
    
    if 'grappelli' in settings.INSTALLED_APPS:
        inline_classes = ('grp-collapse grp-open',) 


class LayerAdmin(BaseLayerAdmin):
    inlines = [LayerExternalInline]
    # custom admin template
    change_form_template = '%s/templates/admin/layer_change_form.html' % os.path.dirname(os.path.realpath(__file__))

admin.site.unregister(Layer)
admin.site.register(Layer, LayerAdmin)