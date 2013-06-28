from django.conf.urls import patterns, include, url


urlpatterns = patterns('nodeshot.community.profiles.views',
    url(r'^/profiles/$', 'profile_list', name='api_profile_list'),
    url(r'^/profiles/(?P<username>.+)/$', 'profile_detail', name='api_profile_detail'),
    
    url(r'^/account/$', 'account_detail', name='api_account_detail'),
    url(r'^/account/password/$', 'account_password_change', name='api_account_password_change'),
    url(r'^/account/password/reset/$', 'account_password_reset', name='api_account_password_reset'),
    url(r'^/account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        'account_password_reset_key',
        name='api_account_password_reset_key'
    ),
)