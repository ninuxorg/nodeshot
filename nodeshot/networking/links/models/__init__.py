"""
Dependencies:
    * nodeshot.core.nodes
    * nodeshot.networking.net
"""

from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'nodeshot.core.nodes',
        'nodeshot.core.layers',
        'nodeshot.networking.net'
    ],
    module='nodeshot.networking.links'
)


from .link import Link


__all__ = ['Link']


# ------ Add relationship to NodeDetailSerializer ------ #

from nodeshot.core.nodes.serializers import ExtensibleNodeSerializer

ExtensibleNodeSerializer.add_relationship(**{
    'name': 'links',
    'view_name': 'api_node_links',
    'lookup_field': 'slug'
})
