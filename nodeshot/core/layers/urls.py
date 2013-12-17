from django.conf.urls import patterns, url
#from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns('nodeshot.core.layers.views',
    url(r'^layers/$', 'layer_list', name='api_layer_list'),
    url(r'^layers/(?P<slug>[-\w]+)/$', 'layer_detail', name='api_layer_detail'),
    url(r'^layers/(?P<slug>[-\w]+)/nodes/$', 'nodes_list', name='api_layer_nodes_list'),
    url(r'^layers/(?P<slug>[-\w]+)/nodes.geojson$', 'nodes_geojson_list', name='api_layer_nodes_geojson'),
    url(r'^layers.geojson$', 'layers_geojson_list', name='api_layer_geojson'),
    url(r'^layers/(?P<slug>[-\w]+)/status_icons/$', 'layer_status_icon_list', name='api_layer_status_icon_list'),
    url(r'^layers.status_icons/$', 'all_layer_status_icon_list', name='api_all_layer_status_icon_list'),
)

#urlpatterns = format_suffix_patterns(urlpatterns)