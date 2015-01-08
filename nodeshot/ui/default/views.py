from django.shortcuts import render

from rest_framework.renderers import JSONRenderer

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Status
from nodeshot.core.cms.models import MenuItem
from nodeshot.core.layers.serializers import LayerListSerializer
from nodeshot.core.nodes.serializers import StatusListSerializer
from nodeshot.core.cms.serializers import MenuSerializer
from nodeshot.community.profiles.serializers import ProfileSerializer

from . import settings as ui_settings


def index(request):
    # django-rest-framework serializer context
    serializer_context = {'request': request}
    # load models
    layers = Layer.objects.published()
    status = Status.objects.all()
    menu = MenuItem.objects.published().filter(parent=None).accessible_to(request.user)
    # initialize serializers
    layers = LayerListSerializer(layers, many=True, context=serializer_context).data
    status = StatusListSerializer(status, many=True, context=serializer_context).data
    menu = MenuSerializer(menu, many=True, context=serializer_context).data
    # initialize user serializer if authenticated
    if request.user.is_authenticated():
        user = ProfileSerializer(request.user, many=False, context=serializer_context).data
    else:
        user = {}
    # initialize django-rest-framework JSON renderer
    json = JSONRenderer()
    # template context
    context = {
        # preloaded data
        'layers': json.render(layers),
        'legend': json.render(status),
        'menu': json.render(menu),
        'user': json.render(user),
        # settings
        'SITE_URL': ui_settings.settings.SITE_URL,
        'MAP_CENTER': ui_settings.MAP_CENTER,
        'MAP_ZOOM': ui_settings.MAP_ZOOM,
        'LEAFLET_OPTIONS': json.render(ui_settings.LEAFLET_OPTIONS),
        'DISABLE_CLUSTERING_AT_ZOOM': ui_settings.DISABLE_CLUSTERING_AT_ZOOM,
        'MAX_CLUSTER_RADIUS': ui_settings.MAX_CLUSTER_RADIUS,
        'DATETIME_FORMAT': ui_settings.DATETIME_FORMAT,
        'DATE_FORMAT': ui_settings.DATE_FORMAT,
        'ADDRESS_SEARCH_TRIGGERS': ui_settings.ADDRESS_SEARCH_TRIGGERS,
        # participation settings
        'VOTING_ENABLED': ui_settings.VOTING_ENABLED,
        'RATING_ENABLED': ui_settings.RATING_ENABLED,
        'COMMENTS_ENABLED': ui_settings.COMMENTS_ENABLED,
        # social auth settings
        'SOCIAL_AUTH_ENABLED': ui_settings.SOCIAL_AUTH_ENABLED,
        'FACEBOOK_ENABLED': ui_settings.FACEBOOK_ENABLED,
        'GOOGLE_ENABLED': ui_settings.GOOGLE_ENABLED,
        'GITHUB_ENABLED': ui_settings.GITHUB_ENABLED,
        # websockets settings
        'WEBSOCKETS': ui_settings.WEBSOCKETS,
        # profiles settings
        'REGISTRATION_OPEN': ui_settings.REGISTRATION_OPEN
    }
    return render(request, 'index.html', context)
