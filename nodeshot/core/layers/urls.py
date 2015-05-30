from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.core.layers.views',
    url(r'^layers/$', 'layer_list', name='api_layer_list'),
    url(r'^layers/(?P<slug>[-\w]+)/$', 'layer_detail', name='api_layer_detail'),
    url(r'^layers/(?P<slug>[-\w]+)/nodes/$', 'nodes_list', name='api_layer_nodes_list'),
    url(r'^layers/(?P<slug>[-\w]+)/nodes.geojson$', 'nodes_geojson_list', name='api_layer_nodes_geojson'),
    url(r'^layers.geojson$', 'layers_geojson_list', name='api_layer_geojson'),
)
