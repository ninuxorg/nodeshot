from tastypie.resources import ModelResource
from tastypie import fields
from models import Device

class DeviceResource(ModelResource):
    node = fields.ForeignKey('nodeshot.core.nodes.resources.NodeResource', 'node')
    
    class Meta:
        queryset = Device.objects.select_related().all().only('id', 'name', 'type', 'status', 'description', 'firmware', 'os', 'node__id', 'node__slug')
        resource_name = 'devices'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated', 'access_level', 'notes']
    
    def dehydrate(self, bundle):
        # node slug instead of URI to save bandwidth
        bundle.data['node'] = bundle.obj.node.slug
    
        return bundle

