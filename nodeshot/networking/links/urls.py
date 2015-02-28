from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.networking.links.views',  # noqa
    url(r'^links/$', 'link_list', name='api_link_list'),
    url(r'^links/(?P<pk>[0-9]+)/$', 'link_details', name='api_link_details'),
    # geojson
    url(r'^links.geojson$', 'link_geojson_list', name='api_links_geojson_list'),
    url(r'^links/(?P<pk>[0-9]+).geojson$', 'link_geojson_details', name='api_links_geojson_details'),
    # node links
    url(r'^nodes/(?P<slug>[-\w]+)/links/$', 'node_link_list', name='api_node_links'),
)
