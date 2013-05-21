from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns('nodeshot.core.nodes.views',
    url(r'^/nodes/$', 'list', name='api_node_list'),
    url(r'^/nodes/geojson/$', 'geojson_list', name='api_node_gejson_list'),
    url(r'^/nodes/(?P<slug>[-\w]+)/$', 'details', name='api_node_details'),
)

urlpatterns = format_suffix_patterns(urlpatterns)