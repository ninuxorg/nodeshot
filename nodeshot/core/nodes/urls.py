from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns('nodeshot.core.nodes.views',
    url(r'^/nodes/$', 'node_list', name='api_node_list'),
    url(r'^/nodes/geojson/$', 'geojson_list', name='api_node_gejson_list'),
    url(r'^/nodes/(?P<slug>[-\w]+)/$', 'node_details', name='api_node_details'),
    
    # images
    url(r'^/nodes/(?P<slug>[-\w]+)/images/$', 'node_images', name='api_node_images'),
)

urlpatterns = format_suffix_patterns(urlpatterns)