# this app is dependant on "net"
from django.conf import settings

if 'nodeshot.core.nodes' not in settings.INSTALLED_APPS:
    raise DependencyError('nodeshot.community.mailing depends on nodeshot.core.nodes, which should be in settings.INSTALLED_APPS')

from inward import Inward
from outward import Outward

__all__ = [
    'Inward',
    'Outward',
]