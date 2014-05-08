from django.contrib import admin
from django.conf import settings

from nodeshot.core.layers.admin import  LayerAdmin
from nodeshot.core.nodes.admin import NodeAdmin

from models import LayerExternal, NodeExternal


class LayerExternalInline(admin.StackedInline):
    model = LayerExternal
    fk_name = 'layer'

    if 'grappelli' in settings.INSTALLED_APPS:
        inline_classes = ('grp-collapse grp-open',)


# add inline to LayerAdmin
LayerAdmin.inlines.append(LayerExternalInline)
# custom admin template
LayerAdmin.change_form_template = 'admin/layer_change_form.html'


class NodeExternalInline(admin.StackedInline):
    model = NodeExternal
    fk_name = 'node'
    extra = 0

NodeAdmin.inlines.append(NodeExternalInline)
