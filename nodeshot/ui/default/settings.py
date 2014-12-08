import json
from django.conf import settings
from leaflet import app_settings as leaflet_settings


TILESERVER_URL = leaflet_settings['TILES'][0][1]
MAP_ZOOM = leaflet_settings['DEFAULT_ZOOM']
MAP_CENTER = list(leaflet_settings['DEFAULT_CENTER'])

if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
    VOTING_ENABLED = getattr(settings, 'NODESHOT_UI_VOTING_ENABLED', True)
    RATING_ENABLED = getattr(settings, 'NODESHOT_UI_RATING_ENABLED', True)
    COMMENTS_ENABLED = getattr(settings, 'NODESHOT_UI_COMMENTS_ENABLED', True)
else:
    VOTING_ENABLED = False
    RATING_ENABLED = False
    COMMENTS_ENABLED = False

VOTING_ENABLED = json.dumps(VOTING_ENABLED)
RATING_ENABLED = json.dumps(RATING_ENABLED)
COMMENTS_ENABLED = json.dumps(COMMENTS_ENABLED)

if 'social_auth' in settings.INSTALLED_APPS:
    FACEBOOK_ENABLED = bool(settings.FACEBOOK_APP_ID) and bool(settings.FACEBOOK_API_SECRET)  # noqa
    GOOGLE_ENABLED = bool(settings.GOOGLE_OAUTH2_CLIENT_ID) and bool(settings.GOOGLE_OAUTH2_CLIENT_SECRET)  # noqa
    GITHUB_ENABLED = bool(settings.GITHUB_APP_ID) and bool(settings.GITHUB_API_SECRET)  # noqa
    SOCIAL_AUTH_ENABLED = FACEBOOK_ENABLED or GOOGLE_ENABLED or GITHUB_ENABLED  # noqa
else:
    FACEBOOK_ENABLED = False
    GOOGLE_ENABLED = False
    GITHUB_ENABLED = False
    SOCIAL_AUTH_ENABLED = False

if 'nodeshot.core.websockets' in settings.INSTALLED_APPS:
    from nodeshot.core.websockets import DOMAIN, PATH, PORT

    WEBSOCKETS = {
        'DOMAIN': DOMAIN,
        'PATH': PATH,
        'PORT': PORT
    }
else:
    WEBSOCKETS = False

from nodeshot.community.profiles.settings import REGISTRATION_OPEN  # noqa
