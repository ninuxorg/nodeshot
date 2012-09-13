from tastypie.resources import ModelResource
from models import Node, Image

class NodeResource(ModelResource):
    class Meta:
        queryset = Node.objects.all()
        resource_name = 'nodes'
        excludes = ['user', 'description', 'notes', 'added', 'updated', 'access_level']
    
    def dehydrate(self, bundle):
        # If they're requesting their own record, add in their email address.
        if self:
            # Note that there isn't an ``email`` field on the ``Resource``.
            # By this time, it doesn't matter, as the built data will no
            # longer be checked against the fields on the ``Resource``.
            bundle.data.pop('resource_uri')
            
            if self.get_resource_uri(bundle) == bundle.request.path:
                bundle.data['user'] = bundle.obj.user.username
                bundle.data['description'] = bundle.obj.description
                bundle.data['added'] = bundle.obj.added
    
            #if self.get_resource_uri(bundle) != bundle.request.path:
            #    print "Not Detail - Could be list or reverse relationship."
    
        return bundle

class ImageResource(ModelResource):
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'images'
        #excludes = ['user', 'description', 'notes', 'added', 'updated', 'access_level']
    
    def dehydrate(self, bundle):
        # If they're requesting their own record, add in their email address.
        if self:
            # Note that there isn't an ``email`` field on the ``Resource``.
            # By this time, it doesn't matter, as the built data will no
            # longer be checked against the fields on the ``Resource``.
            bundle.data.pop('resource_uri')
            
            #if self.get_resource_uri(bundle) == bundle.request.path:
            #    bundle.data['user'] = bundle.obj.user.username
            #    bundle.data['description'] = bundle.obj.description
            #    bundle.data['added'] = bundle.obj.added
    
            #if self.get_resource_uri(bundle) != bundle.request.path:
            #    print "Not Detail - Could be list or reverse relationship."
    
        return bundle

