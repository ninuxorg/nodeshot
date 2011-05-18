from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', 'ns.views.index'),
     (r'^node_list.json', 'ns.views.node_list'),
     (r'^nodes.json', 'ns.views.nodes'),
     (r'^generate_rrd', 'ns.views.generate_rrd'),
     (r'^info_window/(?P<nodeName>\w+)/$', 'ns.views.info_window'),
     (r'^info_tab', 'ns.views.info'),
     (r'^node_form', 'ns.forms.node_form'),
     (r'^device_form', 'ns.forms.device_form'), 
     (r'^configuration_form', 'ns.forms.configuration_form'),


     (r'^admin/', include(admin.site.urls)),
)
