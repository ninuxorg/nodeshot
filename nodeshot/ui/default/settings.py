import json
from django.conf import settings
from leaflet import app_settings as LEAFLET_SETTINGS


TILESERVER_URL = LEAFLET_SETTINGS['TILES'][0][1]
MAP_ZOOM = LEAFLET_SETTINGS['DEFAULT_ZOOM']
MAP_CENTER = list(LEAFLET_SETTINGS['DEFAULT_CENTER'])

if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
    VOTING_ENABLED = getattr(settings, 'NODESHOT_UI_VOTING_ENABLED', True)
else:
    VOTING_ENABLED = False

VOTING_ENABLED = json.dumps(VOTING_ENABLED)
