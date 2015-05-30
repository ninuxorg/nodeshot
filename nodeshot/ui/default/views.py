import json
from django.shortcuts import render

from rest_framework.renderers import JSONRenderer

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Status
from nodeshot.core.cms.models import MenuItem
from nodeshot.core.layers.serializers import LayerDetailSerializer
from nodeshot.core.nodes.serializers import StatusListSerializer
from nodeshot.core.cms.serializers import MenuSerializer
from nodeshot.community.profiles.serializers import ProfileOwnSerializer

from nodeshot.core.nodes.settings import HSTORE_SCHEMA as NODES_HSTORE_SCHEMA
from . import settings as ui_settings


NODES_HSTORE_SCHEMA = NODES_HSTORE_SCHEMA[:] if NODES_HSTORE_SCHEMA is not None else []
for field in NODES_HSTORE_SCHEMA:
    try:
        field['label'] = field['kwargs']['verbose_name']
    except KeyError:
        field['label'] = field['name'].capitalize().replace('_', ' ')

if 'nodeshot.networking.links' in ui_settings.settings.INSTALLED_APPS:
    LINKS_ENABLED = True
    from nodeshot.networking.links.utils import links_legend
else:
    LINKS_ENABLED = False


def index(request):
    # django-rest-framework serializer context
    serializer_context = {'request': request}
    # load models
    layers = Layer.objects.published()
    status = Status.objects.all()
    menu = MenuItem.objects.published().filter(parent=None).accessible_to(request.user)
    # initialize serializers
    layers = LayerDetailSerializer(layers, many=True, context=serializer_context).data
    status = StatusListSerializer(status, many=True, context=serializer_context).data
    menu = MenuSerializer(menu, many=True, context=serializer_context).data
    # initialize user serializer if authenticated
    if request.user.is_authenticated():
        user = ProfileOwnSerializer(request.user, many=False, context=serializer_context).data
    else:
        user = {}
    # add link legend
    if LINKS_ENABLED:
        status += links_legend
    # initialize django-rest-framework JSON renderer
    json_renderer = JSONRenderer()
    # template context
    context = {
        # preloaded data
        'layers': json_renderer.render(layers),
        'legend': json_renderer.render(status),
        'menu': json_renderer.render(menu),
        'user': json_renderer.render(user),
        # settings
        'SITE_NAME': ui_settings.settings.SITE_NAME,
        'SITE_URL': ui_settings.settings.SITE_URL,
        'MAP_CENTER': ui_settings.MAP_CENTER,
        'MAP_ZOOM': ui_settings.MAP_ZOOM,
        'LEAFLET_OPTIONS': json.dumps(ui_settings.LEAFLET_OPTIONS),
        'DISABLE_CLUSTERING_AT_ZOOM': ui_settings.DISABLE_CLUSTERING_AT_ZOOM,
        'MAX_CLUSTER_RADIUS': ui_settings.MAX_CLUSTER_RADIUS,
        'DATETIME_FORMAT': ui_settings.DATETIME_FORMAT,
        'DATE_FORMAT': ui_settings.DATE_FORMAT,
        'ADDRESS_SEARCH_TRIGGERS': ui_settings.ADDRESS_SEARCH_TRIGGERS,
        'LOGO': ui_settings.LOGO,
        # participation settings
        'VOTING_ENABLED': ui_settings.VOTING_ENABLED,
        'RATING_ENABLED': ui_settings.RATING_ENABLED,
        'COMMENTS_ENABLED': ui_settings.COMMENTS_ENABLED,
        'CONTACTING_ENABLED': ui_settings.CONTACTING_ENABLED,
        # map features (TODO: currently unimplemented)
        'MAP_3D_ENABLED': ui_settings.MAP_3D_ENABLED,
        'MAP_TOOLS_ENABLED': ui_settings.MAP_TOOLS_ENABLED,
        'MAP_PREFERENCES_ENABLED': ui_settings.MAP_PREFERENCES_ENABLED,
        # social auth settings
        'SOCIAL_AUTH_ENABLED': ui_settings.SOCIAL_AUTH_ENABLED,
        'FACEBOOK_ENABLED': ui_settings.FACEBOOK_ENABLED,
        'GOOGLE_ENABLED': ui_settings.GOOGLE_ENABLED,
        'GITHUB_ENABLED': ui_settings.GITHUB_ENABLED,
        # websockets settings
        'WEBSOCKETS': ui_settings.WEBSOCKETS,
        # profiles settings
        'REGISTRATION_OPEN': ui_settings.REGISTRATION_OPEN,
        # additional node fields
        'NODES_HSTORE_SCHEMA': json.dumps(NODES_HSTORE_SCHEMA if NODES_HSTORE_SCHEMA else []),
        # analytics
        'GOOGLE_ANALYTICS_UA': ui_settings.GOOGLE_ANALYTICS_UA,
        'GOOGLE_ANALYTICS_OPTIONS': json.dumps(ui_settings.GOOGLE_ANALYTICS_OPTIONS),
        'PIWIK_ANALYTICS_BASE_URL': ui_settings.PIWIK_ANALYTICS_BASE_URL,
        'PIWIK_ANALYTICS_SITE_ID': ui_settings.PIWIK_ANALYTICS_SITE_ID,
        # miscellaneous
        'ADDITIONAL_GEOJSON_URLS': json.dumps(ui_settings.ADDITIONAL_GEOJSON_URLS),
        'PRIVACY_POLICY_LINK': ui_settings.PRIVACY_POLICY_LINK,
        'TERMS_OF_SERVICE_LINK': ui_settings.TERMS_OF_SERVICE_LINK,
        # networking
        'LINKS_ENABLED': LINKS_ENABLED,
        # metrics
        'METRICS_ENABLED': ui_settings.METRICS_ENABLED
    }
    return render(request, 'index.html', context)
