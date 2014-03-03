from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from filebrowser.sites import site

admin.autodiscover()


urlpatterns = patterns('',
   url(r'^admin/filebrowser/', include(site.urls)),
)


if 'social_auth' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'', include('social_auth.urls')),
    )


if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'^grappelli/', include('grappelli.urls')),
    )


if 'nodeshot.core.websockets' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'^websockets/', include('nodeshot.core.websockets.urls')),
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
    
    urlpatterns = urlpatterns + patterns('',
        url(r'', include('nodeshot.core.api.urls')),
    )


# todo: review
if 'nodeshot.open311.interface' in settings.INSTALLED_APPS:
    urlpatterns += patterns('nodeshot.open311.interface.views',
        url(r'^open311/', 'map_view', name='home'),
    )


if 'nodeshot.ui.default' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'^', include('nodeshot.ui.default.urls', namespace='ui', app_name='ui')),
    )
    
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )