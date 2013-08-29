from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.networking.net.views',
    url(r'^/devices/$', 'device_list', name='api_device_list'),
    url(r'^/devices/(?P<pk>[0-9]+)/$', 'device_details', name='api_device_details'),
    url(r'^/nodes/(?P<slug>[-\w]+)/devices/$', 'node_device_list', name='api_node_devices'),
    
    # interfaces
    url(r'^/devices/(?P<pk>[0-9]+)/ethernet/$', 'device_ethernet_list', name='api_device_ethernet'),
    url(r'^/ethernet/(?P<pk>[0-9]+)/$', 'ethernet_details', name='api_ethernet_details'),
    url(r'^/devices/(?P<pk>[0-9]+)/wireless/$', 'device_wireless_list', name='api_device_wireless'),
    url(r'^/wireless/(?P<pk>[0-9]+)/$', 'wireless_details', name='api_wireless_details'),
    
    # ip
    url(r'^/interfaces/(?P<pk>[0-9]+)/ip/$', 'interface_ip_list', name='api_interface_ip'),
)