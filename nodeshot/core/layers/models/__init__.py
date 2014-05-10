from nodeshot.core.base.utils import check_dependencies
from layer import Layer


__all__ = ['Layer']


check_dependencies(
    dependencies='nodeshot.core.nodes',
    module='nodeshot.core.layers'
)


# ------ Add relationship to ExtensibleNodeSerializer ------ #

from nodeshot.core.nodes.serializers import ExtensibleNodeSerializer

ExtensibleNodeSerializer.add_relationship(**{
    'name': 'layer',
    'view_name': 'api_layer_detail',
    'lookup_field': 'layer.slug'
})
