from django.contrib import admin
from django.utils.translation import ugettext as _

from nodeshot.core.layers.admin import  LayerAdmin
from nodeshot.core.nodes.admin import NodeAdmin

from .models import LayerExternal, NodeExternal
from .settings import settings
from .tasks import synchronize_external_layers


class LayerExternalInline(admin.StackedInline):
    model = LayerExternal
    fk_name = 'layer'

    if 'grappelli' in settings.INSTALLED_APPS:
        inline_classes = ('grp-collapse grp-open',)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Load Synchronizer schema to display specific fields in admin
        """
        if obj is not None:
            try:
                # this is enough to load the new schema
                obj.external
            except LayerExternal.DoesNotExist:
                pass
        return super(LayerExternalInline, self).get_formset(request, obj=None, **kwargs)


def synchronize_action(self, request, queryset):
    synchronized = []
    ignored = []
    for layer in queryset:
        if layer.is_external:
            synchronize_external_layers.apply_async([layer.slug])
            synchronized.append(layer)
        else:
            ignored.append(layer)

    if len(synchronized) == 1:
        synced_message_bit = _("1 layer was synchronized.")
    else:
        synced_message_bit = _("%s layers were synchronized.") % len(synchronized)

    if len(ignored) == 1:
        ignored_message_bit = _("1 layer was ignored because not flagged as external.")
    elif len(ignored) > 1:
        ignored_message_bit = _("%s layers were ignored because not flagged as external.") % len(ignored)
    else:
        ignored_message_bit = ""

    self.message_user(request, "%s %s" % (synced_message_bit, ignored_message_bit), fail_silently=True)
synchronize_action.short_description = _("Synchronize layer (external only)")


# add inline to LayerAdmin
LayerAdmin.inlines.append(LayerExternalInline)
# custom admin template
LayerAdmin.change_form_template = 'admin/layer_change_form.html'
# add synchronize action
LayerAdmin.synchronize_action = synchronize_action
LayerAdmin.actions.append('synchronize_action')


class NodeExternalInline(admin.StackedInline):
    model = NodeExternal
    fk_name = 'node'
    extra = 0

NodeAdmin.inlines.append(NodeExternalInline)
