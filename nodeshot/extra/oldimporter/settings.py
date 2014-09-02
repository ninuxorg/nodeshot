from django.conf import settings


STATUS_MAPPING = getattr(settings, 'NODESHOT_OLDIMPORTER_STATUS_MAPPING', {
    'a': 'active',
    'h': 'active',
    'ah': 'active',
    'p': 'potential',
    'default': 'potential'
})
DEFAULT_LAYER = getattr(settings, 'NODESHOT_OLDIMPORTER_DEFAULT_LAYER', 1)
