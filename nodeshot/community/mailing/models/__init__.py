from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies='nodeshot.core.nodes',
    module='nodeshot.community.mailing'
)


from inward import Inward
from outward import Outward

__all__ = [
    'Inward',
    'Outward',
]


# ------ Add relationship to ExtensibleNodeSerializer ------ #

from nodeshot.core.nodes.serializers import ExtensibleNodeSerializer

ExtensibleNodeSerializer.add_relationship(**{
    'name': 'contact',
    'view_name': 'api_node_contact',
    'lookup_field': 'slug'
})