import os

from django.contrib import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseAdmin, BaseStackedInline
from nodeshot.core.layers.admin import Layer, LayerAdmin
from nodeshot.core.nodes.admin import Node, NodeAdmin

from models import LayerExternal, NodeExternal


class LayerExternalInline(admin.StackedInline):
    model = LayerExternal
    fk_name = 'layer'
    
    if 'grappelli' in settings.INSTALLED_APPS:
        inline_classes = ('grp-collapse grp-open',) 


# add inline to LayerAdmin
LayerAdmin.inlines.append(LayerExternalInline)
# custom admin template
LayerAdmin.change_form_template = '%s/templates/admin/layer_change_form.html' % os.path.dirname(os.path.realpath(__file__))


class NodeExternalInline(admin.StackedInline):
    model = NodeExternal
    fk_name = 'node'
    extra = 0

NodeAdmin.inlines.append(NodeExternalInline)