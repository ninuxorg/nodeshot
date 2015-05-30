from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.core.cms.views',
    url(r'^pages/$', 'page_list', name='api_page_list'),
    url(r'^pages/(?P<slug>[-\w]+)/$', 'page_detail', name='api_page_detail'),
    url(r'^menu/$', 'menu_list', name='api_menu_list'),
)