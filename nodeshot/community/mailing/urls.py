from django.conf.urls import patterns, url
from .settings import settings


urlpatterns = patterns('nodeshot.community.mailing.views',
    # contact node
    url(r'^nodes/(?P<slug>[-\w]+)/contact/$', 'contact_node', name='api_node_contact'),
)


# contact layer
if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    urlpatterns += patterns('nodeshot.community.mailing.views',
        url(r'^layers/(?P<slug>[-\w]+)/contact/$', 'contact_layer', name='api_layer_contact'),
    )


# contact user
if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    urlpatterns += patterns('nodeshot.community.mailing.views',
        url(r'^profiles/(?P<username>[-.\w]+)/contact/$', 'contact_user', name='api_user_contact'),
    )
