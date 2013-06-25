from django.conf.urls import patterns, include, url


urlpatterns = patterns('nodeshot.community.profiles.views',
    url(r'^/profiles/$', 'profile_list', name='api_profile_list'),
    #url(r'^/profiles/(?P<pk>[0-9]+)/$', 'profile_details', name='api_profile_details')
)