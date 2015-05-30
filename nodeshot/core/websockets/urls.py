from django.conf.urls import patterns, url
from django.conf import settings


urlpatterns = patterns('',)


if settings.DEBUG:
    urlpatterns += patterns('nodeshot.core.websockets.views',
        url(r'^test/$', 'test', name='websocket_test'),
    )
