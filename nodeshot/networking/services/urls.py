from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.networking.services.views',
    url(r'^services/categories/$', 'service_category_list', name='api_service_category_list'),
    url(r'^services/categories/(?P<pk>[0-9]+)/$', 'service_category_details', name='api_service_category_details'),
    url(r'^services/$', 'service_list', name='api_service_list'),
    url(r'^services/(?P<pk>[0-9]+)/$', 'service_details', name='api_service_details'),
)
