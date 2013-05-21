from django.conf.urls import patterns, include, url
from django.conf import settings

# importlib is available since python 2.7
from importlib import import_module


urlpatterns = patterns('',)

# loop over all the strings listed in settings.NODESHOT['API']['APPS_ENABLED]
for app_path in settings.NODESHOT['API']['APPS_ENABLED']:
    
    # determine import path for url patterns
    module_path = '%s.urls' % app_path
    
    urlpatterns += patterns('',
        url(r'^%s' % settings.NODESHOT['SETTINGS']['API_PREFIX'], include(module_path))
    )


