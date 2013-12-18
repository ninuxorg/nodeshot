from django.conf.urls import patterns, include, url
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


urlpatterns = patterns('nodeshot.core.api.views',
    url(r'^%s$' % settings.NODESHOT['SETTINGS']['API_PREFIX'], 'root_endpoint', name='api_root_endpoint'),
)

if 'rest_framework_swagger' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^%sdocs/' % settings.NODESHOT['SETTINGS']['API_PREFIX'], include('rest_framework_swagger.urls'))
    )

# loop over all the strings listed in settings.NODESHOT['API']['APPS_ENABLED]
for app_path in settings.NODESHOT['API']['APPS_ENABLED']:
    
    # enable only API modules listed in INSTALLED_APPS
    if app_path not in settings.INSTALLED_APPS:
        # fail silently
        continue
    
    # determine import path for url patterns
    module_path = '%s.urls' % app_path
    
    urlpatterns += patterns('',
        url(r'^%s' % settings.NODESHOT['SETTINGS']['API_PREFIX'], include(module_path))
    )
