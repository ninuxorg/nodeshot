import os
from django.conf import settings


PUBLIC_PIPE = getattr(settings, 'NODESHOT_WEBSOCKETS_PUBLIC_PIPE', '%s/nodeshot.websockets.public' % os.path.dirname(settings.SITE_ROOT))
PRIVATE_PIPE = getattr(settings, 'NODESHOT_WEBSOCKETS_PRIVATE_PIPE', '%s/nodeshot.websockets.private' % os.path.dirname(settings.SITE_ROOT))
DOMAIN = settings.DOMAIN
PATH = getattr(settings, 'NODESHOT_WEBSOCKETS_PATH', '')
LISTENING_ADDRESS = getattr(settings, 'NODESHOT_WEBSOCKETS_LISTENING_ADDRESS', '0.0.0.0')
LISTENING_PORT = getattr(settings, 'NODESHOT_WEBSOCKETS_LISTENING_PORT', 8080)
REGISTER = getattr(settings, 'NODESHOT_WEBSOCKETS_REGISTER', (
    'nodeshot.core.websockets.registrars.nodes',
    'nodeshot.core.websockets.registrars.notifications',
))
