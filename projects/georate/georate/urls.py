from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    # smuggler for fixture management
    # must be before admin url patterns
    url(r'^admin/', include('smuggler.urls')),
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r"^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", "nodeshot.community.profiles.html_views.password_reset_from_key", name="account_password_reset_key"),
)


if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'^grappelli/', include('grappelli.urls')),
    )


# include 'nodeshot.core.api.urls'
if 'nodeshot.core.api' in settings.INSTALLED_APPS:
    
    from nodeshot.core.api.urls import urlpatterns as api_urlpatterns
    
    urlpatterns += api_urlpatterns


if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )