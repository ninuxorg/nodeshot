from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import Link, LinkRadio

class LinkResource(ModelResource):
    
    class Meta:
        queryset = Link.objects.all()
        resource_name = 'links'
        limit = 0
        include_resource_uri = False
            
        excludes = ['added', 'updated']