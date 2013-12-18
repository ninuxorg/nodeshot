from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.open311.views',
    url(r'^open311/services/$',
        'service_list',
        name='api_service_list'),
    
    url(r'^open311/services/(?P<service_type>[-\w]+)/$',
        'service_definition',
        name='api_service_definition'),
    
    url(r'^open311/requests/$',
        'request_list',
        name='api_request_list'),
)