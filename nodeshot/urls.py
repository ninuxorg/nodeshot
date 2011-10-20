# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # public
    url(r'^$', 'nodeshot.views.index', name='nodeshot_index'),
    url(r'^select/(?P<slug>[-\w]+)/$', 'nodeshot.views.index', name='nodeshot_select'),
    url(r'^nodes.json', 'nodeshot.views.nodes', name='nodeshot_nodes'),
    url(r'^jstree.json', 'nodeshot.views.jstree', name='nodeshot_jstree'),
    url(r'^search/(?P<what>.*)/$', 'nodeshot.views.search', name='nodeshot_search'),
    url(r'^node/info/(?P<node_id>\d+)/$', 'nodeshot.views.node_info', name='nodeshot_node_info'),
    url(r'^overview/', 'nodeshot.views.overview', name='nodeshot_overview'), # INFO button on sidebar
    url(r'^node/advanced/(?P<node_id>\d+)/$', 'nodeshot.views.advanced', name='nodeshot_node_advanced'),
    url(r'^node/contact/(?P<node_id>\d+)/$', 'nodeshot.views.contact', name='nodeshot_contact_node'),
    url(r'^tab3/', 'nodeshot.views.extra_tab', {'tab': 3}, name='nodeshot_tab3'),
    url(r'^tab4/', 'nodeshot.views.extra_tab', {'tab': 4}, name='nodeshot_tab3'),
    url(r'^nodes.kml', 'nodeshot.views.generate_kml', name='nodeshot_generate_kml'),
    # this might be implemented in a future version
    #url(r'^generate_rrd', 'nodeshot.views.generate_rrd', name='nodeshot_generate_rrd'),
    
    # private
    url(r'^node/add/', 'nodeshot.views.add_node', name='nodeshot_node_add'),
    url(r'^node/authenticate/(?P<node_id>\d+)/$', 'nodeshot.views.auth_node', name='nodeshot_auth_node'),
    url(r'^node/edit/(?P<node_id>\d+)/(?P<password>.*)/$', 'nodeshot.views.edit_node', name='nodeshot_edit_node'),
    url(r'^node/edit/interface/(?P<node_id>\d+)/(?P<password>.*)/$', 'nodeshot.views.configuration', {'type': 'interface'},name='nodeshot_edit_interfaces'),
    url(r'^node/edit/hna/(?P<node_id>\d+)/(?P<password>.*)/$', 'nodeshot.views.configuration', {'type': 'hna'},name='nodeshot_edit_hna'),
    url(r'^node/reset_password/(?P<node_id>\d+)/', 'nodeshot.views.reset_password', name='nodeshot_reset_password'),
    url(r'^node/edit/device/(?P<node_id>\d+)/(?P<password>.*)/$', 'nodeshot.views.device_form', name='nodeshot_edit_devices'),
    url(r'^node/delete/(?P<node_id>\d+)/(?P<password>.*)/$', 'nodeshot.views.delete_node', name='nodeshot_delete_node'),
    url(r'^node/confirm/(?P<node_id>\d+)/(?P<activation_key>\w+)/$', 'nodeshot.views.confirm_node', name='nodeshot_confirm_node'),
    url(r'^node/report-abuse/(?P<node_id>\d+)/(?P<email>.*)/$', 'nodeshot.views.report_abuse', name='nodeshot_report_abuse'),
    
    # crons
    url(r'^cron/purge_expired/$', 'nodeshot.views.purge_expired', name='nodeshot_purge_expired'),
)
