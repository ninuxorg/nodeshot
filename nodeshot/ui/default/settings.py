from django.conf import settings
# TODO: improve consistency
from nodeshot.core.base.settings import ADMIN_MAP_COORDINATES as MAP_CENTER


TILESERVER_URL = getattr(settings, 'NODESHOT_UI_TILESERVER_URL', '//otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png')
MAP_ZOOM = getattr(settings, 'NODESHOT_FRONTEND_MAP_ZOOM', 4)
