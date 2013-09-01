"""
Dependencies:
    * nodeshot.core.nodes
    * nodeshot.networking.net
"""

from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=['nodeshot.core.nodes', 'nodeshot.networking.net'],
    module='nodeshot.networking.links'
)