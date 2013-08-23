from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.networking.net.views',
    url(r'^/devices/$', 'device_list', name='api_device_list'),
    #url(r'^(?P<pk>[0-9]+)/$', 'location_details', name='api_location_details'),
    #
    ## geojson
    #url(r'^geojson/$', 'geojson_location_list', name='api_geojson_location_list'),
    #url(r'^geojson/(?P<pk>[0-9]+)/$', 'geojson_location_details', name='api_geojson_location_details'),
)