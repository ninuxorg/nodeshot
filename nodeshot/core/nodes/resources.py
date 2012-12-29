from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie.http import HttpNotFound
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.utils.urls import trailing_slash
from models import Node, Image
from nodeshot.core.base.resources import BaseSlugResource, BaseExtraResource
from models.choices import NODE_STATUS
from django.conf import settings

if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
    from nodeshot.core.zones.models import Zone

#from tastypie.paginator import Paginator
#class TestPaginator(Paginator):
#    def page(self):
#        output = super(TestPaginator, self).page()
#        del output['meta']
#        return output   


class NodeResource(BaseSlugResource, BaseExtraResource):
    zone = fields.ForeignKey('nodeshot.core.zones.resources.ZoneResource', 'zone')
    
    class Meta:
        queryset = Node.objects.all().select_related()
        resource_name = 'nodes'
        limit = 0
        include_resource_uri = False
        #paginator_class = TestPaginator
            
        excludes = ['id', 'slug', 'notes', 'updated', 'access_level']
        
        filtering = {
            'zone': ALL,
            'status': ALL,
            'is_hotspot': ALL,
        }
        
        extra = {
            'status': NODE_STATUS
        }
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def dehydrate(self, bundle):
        # username
        bundle.data['user'] = bundle.obj.user.username
        # zone slug instead of URI to save bandwidth
        bundle.data['zone'] = bundle.obj.zone.slug
        
        # if in list of zones
        if self.get_slug_detail_uri(bundle) != bundle.request.path:
            del bundle.data['user']
            del bundle.data['description']
            del bundle.data['avatar']
            del bundle.data['added']
            bundle.data['details'] = self.get_slug_detail_uri(bundle)
        
        return bundle
    
    # zone specific goodies
    if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
        
        def prepend_urls(self):
            return [
                url(r"^zones/(?P<zone_slug>[\w\d_.-]+)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('get_zone_nodes'), name="api_get_zone_nodes"),
            ]
        
        def get_zone_nodes(self, request, **kwargs):
            """ view that gets the nodes of a zone """
            zone_slug = kwargs.get('zone_slug')
            # get object or 404
            try:
                zone = Zone.objects.only('id','slug').get(slug=zone_slug)
            except ObjectDoesNotExist:
                return HttpNotFound()
            # change queryset
            self._meta.queryset = Node.objects.filter(zone_id=zone.id)
            # return list of nodes
            return self.get_list(request)


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
        excludes = ['added', 'updated', 'access_level', 'order']
        
        filtering = {
            'node': ALL,
        }

    def get_node_images(self, request, **kwargs):
        """ images of a node """
        slug = kwargs.pop('node_slug')
        
        try:
            node = Node.objects.only('id', 'slug').get(slug=slug)
        except ObjectDoesNotExist:
            return HttpNotFound()
            
        self._meta.queryset = Image.objects.filter(node_id=node.id)

        return self.get_list(request)

    def dehydrate(self, bundle):
        # if retrieving images of a node 
        if '/nodes/' in bundle.request.path:
            # del node slug as it's always the same for each image
            del bundle.data['node']
        # if retrieving all images
        else:
            # node slug instead of URI to save space
            bundle.data['node'] = bundle.obj.node.slug
        
        # if description is empty
        if bundle.data['description'] == '':
            del bundle.data['description']
        
        return bundle