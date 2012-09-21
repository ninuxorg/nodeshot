from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.http import HttpNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls.defaults import url
from models import RoutingProtocol, Device, Interface, Ip
from nodeshot.core.nodes.models import Node

class RoutingProtocolResource(ModelResource):  
    class Meta:
        queryset = RoutingProtocol.objects.all()#.only('id', 'name', 'type', 'status', 'description', 'firmware', 'os', 'node__id', 'node__slug')
        resource_name = 'routing-protocols'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated']

class DeviceResource(ModelResource):
    node = fields.ForeignKey('nodeshot.core.nodes.resources.NodeResource', 'node')
    
    class Meta:
        queryset = Device.objects.select_related().all().only('id', 'name', 'type', 'status', 'description', 'firmware', 'os', 'node__id', 'node__slug')
        resource_name = 'devices'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated', 'access_level', 'notes']
        
        filtering = {
            'node': ALL,
        }
    
    def override_urls(self):
        return [
            url(r"^nodes/(?P<node_slug>[\w\d_.-]+)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('get_node_devices'), name="api_get_node_devices"),
        ]
    
    def dehydrate(self, bundle):
        # node slug instead of URI to save bandwidth
        bundle.data['node'] = bundle.obj.node.slug
    
        return bundle

    def get_node_devices(self, request, **kwargs):
        """ devices of a node """
        slug = kwargs.pop('node_slug')
        
        try:
            node = Node.objects.get(slug=slug).only('id')
        except ObjectDoesNotExist:
            return HttpNotFound()
            
        filters = request.GET.copy()
        filters['node'] = node.pk
        request.GET = filters

        return self.get_list(request)

class InterfaceResource(ModelResource):
    device = fields.ForeignKey('nodeshot.core.network.resources.DeviceResource', 'device')
    
    class Meta:
        queryset = Interface.objects.select_related().all()#.only('id', 'name', 'type', 'status', 'description', 'firmware', 'os', 'node__id', 'node__slug')
        resource_name = 'interfaces'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated', 'access_level']
        
        filtering = {
            'device': ALL,
        }
    
    def dehydrate(self, bundle):
        # ...
        bundle.data['device'] = bundle.obj.device.id
    
        return bundle

class IpResource(ModelResource):
    interface = fields.ForeignKey('nodeshot.core.network.resources.InterfaceResource', 'interface')
    
    class Meta:
        queryset = Ip.objects.select_related().all()#.only('id', 'name', 'type', 'status', 'description', 'firmware', 'os', 'node__id', 'node__slug')
        resource_name = 'ip'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated', 'access_level']
        
        filtering = {
            'interface': ALL,
        }
    
    def dehydrate(self, bundle):
        # ...
        bundle.data['interface'] = bundle.obj.interface.id
    
        return bundle