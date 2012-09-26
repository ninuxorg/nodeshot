from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import Service, Category, Login

class ServiceResource(ModelResource):
    
    class Meta:
        queryset = Service.objects.all()
        resource_name = 'services'
        limit = 0
        include_resource_uri = False
            
        excludes = ['added', 'updated', 'access_level']

class CategoryResource(ModelResource):
    
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        limit = 0
        include_resource_uri = False
            
        excludes = ['added', 'updated']

class LoginResource(ModelResource):
    
    class Meta:
        queryset = Login.objects.all()
        resource_name = 'service-logins'
        limit = 0
        include_resource_uri = False
            
        excludes = ['added', 'updated']