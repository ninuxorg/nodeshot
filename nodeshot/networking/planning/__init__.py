# this app is dependant on "net"
from django.conf import settings
if 'nodeshot.networking.net' not in settings.INSTALLED_APPS:
    from nodeshot.core.base.exceptions import DependencyError
    raise DependencyError('nodeshot.networking.hardware depends on nodeshot.networking.net, which should be in settings.INSTALLED_APPS')