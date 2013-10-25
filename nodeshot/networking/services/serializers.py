#from django.conf import settings

from rest_framework import pagination, serializers

from .models import *


__all__ = [
    'ServiceListSerializer',
    'ServiceDetailSerializer',
    'PaginatedServiceSerializer',
    'ServiceLoginSerializer',
    'CategorySerializer'
]


class ServiceLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLogin


class ServiceListSerializer(serializers.ModelSerializer):
    """ Service List Serializer  """
    
    details = serializers.HyperlinkedIdentityField(view_name='api_service_details')
    
    class Meta:
        model = Service
        #fields = ['id', 'line', 'quality', 'details']
        

class ServiceDetailSerializer(ServiceListSerializer):
    """ Service Detail Serializer  """
    
    logins = ServiceLoginSerializer(many=True, source='servicelogin_set')
    
    class Meta:
        model = Service
        #fields = ['id', 'line', 'quality', 'details']


class PaginatedServiceSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = ServiceListSerializer


class CategorySerializer(serializers.ModelSerializer):
    
    details = serializers.HyperlinkedIdentityField(view_name='api_service_category_details')
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'added', 'updated', 'details']