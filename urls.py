# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('nodeshot.urls')),
#    (r'^$', 'nodeshot.views.index'),
#    (r'^node_list.json', 'nodeshot.views.node_list'),
#    (r'^nodes.json', 'nodeshot.views.nodes'),
#    (r'^search/(?P<what>.*)$', 'nodeshot.views.search'),
#    (r'^generate_rrd', 'nodeshot.views.generate_rrd'),
##    (r'^info_window/(?P<nodeName>\w+)$', 'nodeshot.views.info_window'),
#    (r'^info_window/(?P<nodeName>.*)$', 'nodeshot.views.info_window'),
#    (r'^info_tab', 'nodeshot.views.info'),
#    (r'^node_form', 'nodeshot.forms.node_form'),
#    (r'^device_form', 'nodeshot.forms.device_form'), 
#    (r'^configuration_form', 'nodeshot.forms.configuration_form'),

    (r'^admin/', include(admin.site.urls)),
)

# serve static files only if DEBUG and DEVELOPMENT_SERVER are True (in settings.py)
from settings import DEBUG, DEVELOPMENT_SERVER, MEDIA_ROOT
if DEBUG and DEVELOPMENT_SERVER:
  # you might need to change "media" to suit your settings.MEDIA_URL
  urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
  )
