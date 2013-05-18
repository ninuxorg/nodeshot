# this app is dependant on "net"
from django.conf import settings
if 'nodeshot.core.layers' not in settings.INSTALLED_APPS:
    from nodeshot.core.base.exceptions import DependencyError
    raise DependencyError('nodeshot.interoperability depends on nodeshot.core.layers, which should be in settings.INSTALLED_APPS')


from layer_external import LayerExternal

__all__ = ['LayerExternal']