from django.conf import settings


NODES_MINIMUM_DISTANCE = getattr(settings, 'NODESHOT_LAYERS_NODES_MINIMUM_DISTANCE', 0)
REVERSION_ENABLED = getattr(settings, 'NODESHOT_LAYERS_REVERSION_ENABLED', True)
TEXT_HTML = getattr(settings, 'NODESHOT_LAYERS_TEXT_HTML', True)
