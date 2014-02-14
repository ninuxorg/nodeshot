from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.open311.views',
    url(r'^open311/services/$',
        'service_list',
        name='api_service_list'),
    
    url(r'^open311/services/(?P<service_type>[-\w]+)/$',
        'service_definition',
        name='api_service_definition'),
    
    url(r'^open311/requests/$',
        'service_requests',
        name='api_service_requests'),
    
    url(r'^open311/requests/(?P<service_code>[-\w]+)-(?P<request_id>[-\w]+)$',
        'service_request',
        name='api_service_request'),
)