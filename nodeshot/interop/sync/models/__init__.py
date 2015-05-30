from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'django_hstore',
        'nodeshot.core.layers',
        'nodeshot.core.nodes',
    ],
    module='nodeshot.interop.sync'
)


from .layer_external import LayerExternal
from .node_external import NodeExternal


__all__ = ['LayerExternal', 'NodeExternal']


# ------ patch LayerNodesList view to support external layers ------ #

from nodeshot.core.layers.views import LayerNodesList

def get_nodes(self, request, *args, **kwargs):
    try:
        external = self.layer.external
    except LayerExternal.DoesNotExist:
        external = False
    # override view get_nodes method if we have a custom one
    if external and self.layer.is_external and hasattr(external, 'get_nodes'):
        return external.get_nodes(self.__class__.__name__, request.QUERY_PARAMS)
    # otherwise return the standard one
    else:
        return (self.list(request, *args, **kwargs)).data

LayerNodesList.get_nodes = get_nodes
