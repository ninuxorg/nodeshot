from django.conf import settings


HSTORE_SCHEMA = getattr(settings, 'NODESHOT_LAYERS_HSTORE_SCHEMA', None)
NODES_MINIMUM_DISTANCE = getattr(settings, 'NODESHOT_LAYERS_NODES_MINIMUM_DISTANCE', 0)
REVERSION_ENABLED = getattr(settings, 'NODESHOT_LAYERS_REVERSION_ENABLED', True)
TEXT_HTML = getattr(settings, 'NODESHOT_LAYERS_TEXT_HTML', True)


if HSTORE_SCHEMA:
    ADDITIONAL_LAYER_FIELDS = [field.get('name') for field in HSTORE_SCHEMA]
else:
    ADDITIONAL_LAYER_FIELDS = []
