from django.conf import settings


API_PREFIX = getattr(settings, 'NODESHOT_API_PREFIX', 'api/v1/')
API_APPS_ENABLED = getattr(settings, 'NODESHOT_API_APPS_ENABLED', [
    'nodeshot.core.nodes',
    'nodeshot.core.layers',
    'nodeshot.core.cms',
    'nodeshot.community.profiles',
    'nodeshot.community.participation',
    'nodeshot.community.notifications',
    'nodeshot.community.mailing',
    'nodeshot.networking.net',
    'nodeshot.networking.links',
    'nodeshot.networking.services',
    'nodeshot.interop.open311',
])
