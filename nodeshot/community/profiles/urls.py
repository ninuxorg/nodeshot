from django.conf.urls import patterns, url
from .settings import EMAIL_CONFIRMATION


urlpatterns = patterns('nodeshot.community.profiles.views',
    url(r'^profiles/$', 'profile_list', name='api_profile_list'),
    url(r'^profiles/(?P<username>[-.\w]+)/$', 'profile_detail', name='api_profile_detail'),
    url(r'^profiles/(?P<username>[-.\w]+)/nodes/$', 'user_nodes', name='api_user_nodes'),
    url(r'^profiles/(?P<username>[-.\w]+)/social-links/$', 'user_social_links_list', name='api_user_social_links_list'),
    url(r'^profiles/(?P<username>[-.\w]+)/social-links/(?P<pk>[0-9]+)/$', 'user_social_links_detail', name='api_user_social_links_detail'),

    url(r'^account/$', 'account_detail', name='api_account_detail'),
    url(r'^account/login/$', 'account_login', name='api_account_login'),
    url(r'^account/logout/$', 'account_logout', name='api_account_logout'),

    url(r'^account/password/$', 'account_password_change', name='api_account_password_change'),
    url(r'^account/password/reset/$', 'account_password_reset_request_key', name='api_account_password_reset_request_key'),
    url(r'^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', 'account_password_reset_from_key', name='api_account_password_reset_from_key'),
)


# email addresses
if EMAIL_CONFIRMATION:
    urlpatterns += patterns('nodeshot.community.profiles.views',
        url(r'^account/email/$', 'account_email_list', name='api_account_email_list'),
        url(r'^account/email/(?P<pk>[0-9]+)/$', 'account_email_detail', name='api_account_email_detail'),
        url(r'^account/email/(?P<pk>[0-9]+)/resend-confirmation/$', 'account_email_resend_confirmation', name='api_account_email_resend_confirmation'),
    )
