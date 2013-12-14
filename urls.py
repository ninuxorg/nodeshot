# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('nodeshot.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^rosetta/', include('rosetta.urls')),
)

# serve static files only if DEBUG and DEVELOPMENT_SERVER are True (in settings.py)
from settings import DEBUG, DEVELOPMENT_SERVER, MEDIA_ROOT, STATIC_ROOT
if DEBUG and DEVELOPMENT_SERVER:
#   you might need to change "media" to suit your settings.MEDIA_URL
  urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
  )
