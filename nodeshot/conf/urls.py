from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls))
)

if 'smuggler' in settings.INSTALLED_APPS:
    # smuggler must be before admin
    urlpatterns = patterns('',
        url(r'^admin/', include('smuggler.urls'))
    ) + urlpatterns

if 'filebrowser' in settings.INSTALLED_APPS:
    from filebrowser.sites import site
    urlpatterns += patterns('',
        url(r'^admin/filebrowser/', include(site.urls)),
    )

if 'rosetta' in settings.INSTALLED_APPS:
    # rosetta must be before admin
    urlpatterns = patterns('',
        url(r'^admin/translations/', include('rosetta.urls')),
    ) + urlpatterns

if 'nodeshot.interop.sync' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'', include('nodeshot.interop.sync.urls')),
    )

if settings.SERVE_STATIC:
    from django.conf.urls.static import static
    urlpatterns += patterns(url(r'^static/(?P<path>.*)$',
                            'django.contrib.staticfiles.views.serve'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'social.apps.django_app.default' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'', include('social.apps.django_app.urls', namespace='social')),
    )

if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^grappelli/', include('grappelli.urls')),
    )

if 'nodeshot.core.websockets' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^websockets/', include('nodeshot.core.websockets.urls')),
    )

if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
            'nodeshot.community.profiles.html_views.password_reset_from_key',
            name='account_password_reset_from_key'),
    )

    from nodeshot.community.profiles.settings import EMAIL_CONFIRMATION

    if EMAIL_CONFIRMATION:
        urlpatterns += patterns('',
            url(r'^confirm_email/(\w+)/$',
                'nodeshot.community.profiles.html_views.confirm_email',
                name='emailconfirmation_confirm_email'),
        )

if 'nodeshot.core.api' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'', include('nodeshot.core.api.urls')),
    )

if 'nodeshot.ui.open311_demo' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^open311/$', include('nodeshot.ui.open311_demo.urls', namespace='open311_demo', app_name='open311_demo')),
    )

if 'nodeshot.ui.default' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'', include('nodeshot.ui.default.urls', namespace='ui', app_name='ui')),
    )

urlpatterns += patterns('',
    url(r'^jsi18n/$', 'nodeshot.core.base.views.jsi18n', {'packages': ('nodeshot.ui.default',)}, name='jsi18n')
)
