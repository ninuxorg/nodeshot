from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.core.nodes.views',  # noqa
    url(r'^nodes/$', 'node_list', name='api_node_list'),
    url(r'^nodes.geojson$', 'geojson_list', name='api_node_gejson_list'),
    url(r'^nodes/(?P<slug>[-\w]+)/$', 'node_details', name='api_node_details'),

    # images
    url(r'^nodes/(?P<slug>[-\w]+)/images/$', 'node_images', name='api_node_images'),
    url(r'^nodes/(?P<slug>[-\w]+)/images/(?P<pk>[0-9]+)/$', 'node_image_detail', name='api_node_image_detail'),

    # status
    url(r'^status/$', 'status_list', name='api_status_list'),

    # utils
    url(r'^elevation/$', 'elevation_profile', name='api_elevation_profile'),
)
