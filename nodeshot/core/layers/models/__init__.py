from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies='nodeshot.core.nodes',
    module='nodeshot.core.layers'
)

from layer import Layer

__all__ = ['Layer']
