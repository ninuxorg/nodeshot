from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'nodeshot.core.layers',
        'nodeshot.core.nodes',
    ],
    module='nodeshot.interoperability'
)


from .layer_external import LayerExternal


__all__ = ['LayerExternal']