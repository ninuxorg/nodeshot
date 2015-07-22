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
