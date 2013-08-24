from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.networking.net.views',
    url(r'^/devices/$', 'device_list', name='api_device_list'),
    url(r'^/devices/(?P<pk>[0-9]+)/$', 'device_details', name='api_device_details'),

)