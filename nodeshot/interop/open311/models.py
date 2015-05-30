from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'nodeshot.core.nodes',
        'nodeshot.core.layers',
        'nodeshot.community.participation'
    ],
    module='nodeshot.interop.open311'
)
