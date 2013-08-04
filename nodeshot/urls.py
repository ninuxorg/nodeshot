from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',)


if 'social_auth' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'', include('social_auth.urls')),
    )


if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'^grappelli/', include('grappelli.urls')),
    )


if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r"^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
            "nodeshot.community.profiles.html_views.password_reset_from_key",
            name="account_password_reset_key"),
    )


if 'nodeshot.community.profiles' in settings.INSTALLED_APPS and settings.NODESHOT['SETTINGS'].get('PROFILE_EMAIL_CONFIRMATION', True):
    urlpatterns = urlpatterns + patterns('',
        url(r'^confirm_email/(\w+)/$', 'nodeshot.community.profiles.html_views.confirm_email', name='emailconfirmation_confirm_email'),
    )


# include 'nodeshot.core.api.urls'
if 'nodeshot.core.api' in settings.INSTALLED_APPS:
    
    from nodeshot.core.api.urls import urlpatterns as api_urlpatterns
    
    urlpatterns += api_urlpatterns


urlpatterns += patterns('nodeshot.community.participation.views',
    url(r'^$', 'map_view', name='home'),
)