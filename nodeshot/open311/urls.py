from django.conf.urls import patterns, url
#from rest_framework.urlpatterns import format_suffix_patterns
from nodeshot.open311 import views

urlpatterns = patterns('nodeshot.open311.views',
    url(r'^open311/services/$', 'service_list', name='api_service_list'),
    url(r'^open311/services/(?P<slug>[-\w]+)-(?P<service_type>[-\w]+)/$',
        'service_definition',
        name='api_service_definition'),
    url(r'^open311/requests/$', 'request_list', name='api_request_list'),
    #url(r'^layers/(?P<slug>[-\w]+)/nodes/$', 'nodes_list', name='api_layer_nodes_list'),
    #url(r'^layers/(?P<slug>[-\w]+)/nodes.geojson$', 'nodes_geojson_list', name='api_layer_nodes_geojson'),
    #url(r'^layers.geojson$', 'layers_geojson_list', name='api_layer_geojson'),
)

#urlpatterns = format_suffix_patterns(urlpatterns)