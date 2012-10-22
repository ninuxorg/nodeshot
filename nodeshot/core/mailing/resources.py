from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from models import Inward

from django.contrib.contenttypes.models import ContentType


class ContentTypeResource(ModelResource):

    class Meta:
        queryset = ContentType.objects.all()
        resource_name = 'content_type'
        allowed_methods = ['get',]
    
    def dehydrate(self, bundle):
        # detail view
        bundle.data['content_type'] = bundle.obj.id
        return bundle


class InwardResource(ModelResource):
    
    content_type = fields.ToOneField(ContentTypeResource, attribute = 'content_type')
    
    class Meta:
        resource_name = 'contact'
        #allowed_methods = ['post']
        queryset = Inward.objects.all()
        authorization = Authorization()
        authentication = Authentication()
        
    #def dehydrate(self, bundle):
    #    # detail view
    #    bundle.data['content_type'] = bundle.obj.content_type.id
    #    return bundle
    

#from tastypie.resources import ModelResource
#from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
#from tastypie.authorization import Authorization
#from tastypie.authentication import Authentication
#from models import Inward
#
## TODO: dependencies
#from nodeshot.core.zones.models import Zone
#from nodeshot.core.zones.resources import ZoneResource
#from nodeshot.core.nodes.models import Node
#from nodeshot.core.nodes.resources import NodeResource
#
#
#class InwardResource(ModelResource):
#    
#    to = GenericForeignKeyField({
#        Node: NodeResource,
#        Zone: ZoneResource
#    }, 'to')
#    
#    class Meta:
#        resource_name = 'contact'
#        #allowed_methods = ['post']
#        queryset = Inward.objects.all()
#        authorization = Authorization()
#        authentication = Authentication()
#        default_format = 'application/json'
#        
#    def dehydrate(self, bundle):
#        # detail view
#        bundle.data['to'] = bundle.obj.content_type.id
#        return bundle