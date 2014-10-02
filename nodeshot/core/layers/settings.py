from django.conf import settings

NODE_MINIMUM_DISTANCE = getattr(settings, 'NODESHOT_LAYERS_NODE_MINIMUM_DISTANCE', 0)
REVERSION_ENABLED = getattr(settings, 'NODESHOT_LAYERS_REVERSION_ENABLED', True)
TEXT_HTML = getattr(settings, 'NODESHOT_LAYERS_TEXT_HTML', True)
