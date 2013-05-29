from django.conf.urls import patterns, include, url
from django.conf import settings
from nodeshot.community.participation import urls


urlpatterns = patterns('nodeshot.core.api.views',
    url(r'^%s/$' % settings.NODESHOT['SETTINGS']['API_PREFIX'], 'root_endpoint', name='api_root_endpoint'),
)

# loop over all the strings listed in settings.NODESHOT['API']['APPS_ENABLED]
for app_path in settings.NODESHOT['API']['APPS_ENABLED']:
    
    # ensure enabled API module is listed in INSTALLED_APPS
    if app_path in settings.INSTALLED_APPS:
    
        # determine import path for url patterns
        module_path = '%s.urls' % app_path
        
        urlpatterns += patterns('',
            url(r'^%s' % settings.NODESHOT['SETTINGS']['API_PREFIX'], include(module_path))
        )
