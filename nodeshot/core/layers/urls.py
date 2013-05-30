from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns('nodeshot.core.layers.views',
    url(r'^/layers/$', 'list', name='api_layer_list'),
    url(r'^/layers/(?P<slug>[-\w]+)/$', 'details', name='api_layer_details'),
    url(r'^/layers/(?P<slug>[-\w]+)/nodes/$', 'node_list', name='api_layer_nodes_details'),
    url(r'^/layers/(?P<slug>[-\w]+)/geojson/$', 'geojson_list', name='api_layer_nodes_geojson'),
)

#urlpatterns = format_suffix_patterns(urlpatterns)