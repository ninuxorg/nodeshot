from django.shortcuts import render
from django.conf import settings
from nodeshot.core.layers.models import Layer
from . import settings as ui_settings


# TODO: improve ugly code
def index(request):
    layers = Layer.objects.published()
    layers_allowing_new_nodes = layers.filter(new_nodes_allowed=True)

    context = {
        'layers': layers,
        'layers_allowing_new_nodes': layers_allowing_new_nodes,
        'TILESERVER_URL': ui_settings.TILESERVER_URL,
        'MAP_CENTER': ui_settings.MAP_CENTER,
        'MAP_ZOOM': ui_settings.MAP_ZOOM,
        # participation
        'VOTING_ENABLED': ui_settings.VOTING_ENABLED,
        'RATING_ENABLED': ui_settings.RATING_ENABLED,
        'COMMENTS_ENABLED': ui_settings.COMMENTS_ENABLED,
        # social auth
        'SOCIAL_AUTH_ENABLED': ui_settings.SOCIAL_AUTH_ENABLED,
        'FACEBOOK_ENABLED': ui_settings.FACEBOOK_ENABLED,
        'GOOGLE_ENABLED': ui_settings.GOOGLE_ENABLED,
        'GITHUB_ENABLED': ui_settings.GITHUB_ENABLED,
        # websockets
        'WEBSOCKETS': ui_settings.WEBSOCKETS,
    }
    return render(request, 'index.html', context)
