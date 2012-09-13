from django.conf.urls.defaults import url
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import Node, Image

#from tastypie.paginator import Paginator
#class TestPaginator(Paginator):
#    def page(self):
#        output = super(TestPaginator, self).page()
#        del output['meta']
#        return output   

class NodeResource(ModelResource):
    zone = fields.ForeignKey('nodeshot.core.zones.api.ZoneResource', 'zone')
    
    class Meta:
        queryset = Node.objects.all().select_related()
        resource_name = 'nodes'
        limit = 0
        include_resource_uri = False
            
        excludes = ['user', 'description', 'notes', 'added', 'updated', 'access_level']
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
        # If they're requesting their own record, add in their email address.
        if self:
            # Note that there isn't an ``email`` field on the ``Resource``.
            # By this time, it doesn't matter, as the built data will no
            # longer be checked against the fields on the ``Resource``.
            #bundle.data.pop('resource_uri')
            
            if self.get_resource_uri(bundle) == bundle.request.path:
                bundle.data['user'] = bundle.obj.user.username
                bundle.data['description'] = bundle.obj.description
                bundle.data['added'] = bundle.obj.added
            
            bundle.data['zone'] = bundle.obj.zone.slug
    
            #if self.get_resource_uri(bundle) != bundle.request.path:
            #    print "Not Detail - Could be list or reverse relationship."
    
        return bundle

class ImageResource(ModelResource):
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'images'
        include_resource_uri = False
        excludes = ['added', 'updated', 'access_level']

