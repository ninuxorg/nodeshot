from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie.http import HttpNotFound
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.utils.urls import trailing_slash
from models import Node, Image

#from tastypie.paginator import Paginator
#class TestPaginator(Paginator):
#    def page(self):
#        output = super(TestPaginator, self).page()
#        del output['meta']
#        return output   

class NodeResource(ModelResource):
    zone = fields.ForeignKey('nodeshot.core.zones.resources.ZoneResource', 'zone')
    
    class Meta:
        queryset = Node.objects.all().select_related()
        resource_name = 'nodes'
        limit = 0
        include_resource_uri = False
            
        excludes = ['notes', 'updated', 'access_level']
        # = TestPaginator
        
        filtering = {
            'zone': ALL,
            'status': ALL
        }
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def dehydrate(self, bundle):
        # detail view
        if self.get_resource_uri(bundle) == bundle.request.path:
            bundle.data['user'] = bundle.obj.user.username
            # zone slug instead of URI to save bandwidth
            bundle.data['zone'] = bundle.obj.zone.slug
        bundle.data['user'] = bundle.obj.user.username
        # zone slug instead of URI to save bandwidth
        bundle.data['zone'] = bundle.obj.zone.slug
        # if list view
        #bundle.data['yoyo'] = self.get_resource_uri(bundle)
        #else:
        #    #del bundle.data['user']
        #    del bundle.data['description']
        #    del bundle.data['added']
        #    del bundle.data['zone']
        
        return bundle

class ImageResource(ModelResource):
    node = fields.ForeignKey('nodeshot.core.nodes.api.NodeResource', 'node')
    
    def override_urls(self):
        return [
            url(r"^nodes/(?P<node_slug>[\w\d_.-]+)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('get_node_images'), name="api_get_node_images"),
        ]
    
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'images'
        include_resource_uri = False
        limit = 0
        excludes = ['added', 'updated', 'access_level']
        
        filtering = {
            'node': ALL,
        }

    def get_node_images(self, request, **kwargs):
        """ images of a node """
        slug = kwargs.pop('node_slug')
        
        try:
            node = Node.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return HttpNotFound()
            
        filters = request.GET.copy()
        filters['node'] = node.pk
        request.GET = filters

        return self.get_list(request)

    def dehydrate(self, bundle):
        # node slug instead of URI to save space
        bundle.data['node'] = bundle.obj.node.slug
        
        return bundle