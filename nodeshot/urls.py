# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'nodeshot.views.index', name='nodeshot_index'),
    url(r'^select/(?P<slug>[-\w]+)/$', 'nodeshot.views.index', name='nodeshot_select'),
    url(r'^node_list.json', 'nodeshot.views.node_list', name='nodeshot_list_json'),
    url(r'^nodes.json', 'nodeshot.views.nodes', name='nodes_json'),
    url(r'^search/(?P<what>.*)/$', 'nodeshot.views.search', name='nodeshot_search'),
    url(r'^generate_rrd', 'nodeshot.views.generate_rrd', name='nodeshot_generate_rrd'),
    url(r'^kml-feed', 'nodeshot.views.generate_kml', name='nodeshot_generate_kml'),
    url(r'^info_window/(?P<node_id>\d+)/$', 'nodeshot.views.info_window', name='nodeshot_info_window'),
    url(r'^info_tab', 'nodeshot.views.info', name='nodeshot_info_tab'),
    url(r'^node_form', 'nodeshot.forms.node_form', name='nodeshot_node_form'),
    url(r'^edit/(?P<node_id>\d+)/', 'nodeshot.forms.edit_node', name='nodeshot_edit_node'),
    url(r'^recover_password/(?P<node_id>\d+)/', 'nodeshot.views.recover_password', name='nodeshot_recover_password'),
    url(r'^device_form/(?P<node_id>\d+)/$', 'nodeshot.forms.device_form', name='nodeshot_device_form'), 
    url(r'^configuration_form', 'nodeshot.forms.configuration_form', name='nodeshot_configuration_form'),
    url(r'^confirm/(?P<node_id>\d+)/(?P<activation_key>\w+)/$', 'nodeshot.views.confirm_node', name='nodeshot_confirm_node'),
    url(r'^report_abuse/(?P<node_id>\d+)/(?P<email>.*)/$', 'nodeshot.views.report_abuse', name='nodeshot_report_abuse'),
    url(r'^purge_expired/$', 'nodeshot.views.purge_expired', name='nodeshot_purge_expired'),
    url(r'^contact/(?P<node_id>\d+)/$', 'nodeshot.views.contact', name='nodeshot_contact'),
)
