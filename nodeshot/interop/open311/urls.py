from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.interop.open311.views',
    url(r'^open311/$', 'service_discovery', name='api_service_discovery'),
    url(r'^open311/services.json$', 'service_definition_list', name='api_service_definition_list'),
    url(r'^open311/services/(?P<service_type>[-\w]+).json$', 'service_definition_detail', name='api_service_definition_detail'),
    url(r'^open311/requests.json$', 'service_request_list', name='api_service_request_list'),
    url(r'^open311/requests/(?P<service_code>[-\w]+)-(?P<request_id>[-\w]+).json$', 'service_request_detail', name='api_service_request_detail'),
)
