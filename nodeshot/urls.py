# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'nodeshot.views.index'),
    (r'^node_list.json', 'nodeshot.views.node_list'),
    (r'^nodes.json', 'nodeshot.views.nodes'),
    (r'^search/(?P<what>.*)$', 'nodeshot.views.search'),
    (r'^generate_rrd', 'nodeshot.views.generate_rrd'),
    (r'^info_window/(?P<nodeName>.*)$', 'nodeshot.views.info_window'),
    (r'^info_tab', 'nodeshot.views.info'),
    (r'^node_form', 'nodeshot.forms.node_form'),
    (r'^device_form', 'nodeshot.forms.device_form'), 
    (r'^configuration_form', 'nodeshot.forms.configuration_form'),
)