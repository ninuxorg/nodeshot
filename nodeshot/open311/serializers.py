import simplejson as json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_gis import serializers as geoserializers

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.serializers import NodeListSerializer

from .base import Attribute, SERVICES

HSTORE_ENABLED = settings.NODESHOT['SETTINGS'].get('HSTORE', True)

if HSTORE_ENABLED:
    from nodeshot.core.base.fields import HStoreDictionaryField

__all__ = [
    'ServiceNodeSerializer',
    'ServiceListSerializer',
    'RequestListSerializer',
]

ACTIONS = ('node_insert','comment','voting','rating',)
RATING_CHOICES = [ {"key":n,"value":n} for n in range(1, 11) ]
VOTING_CHOICES = [ {"key":1,"value":1}, {"key":-1,"value":-1} ]


class ServiceListSerializer(serializers.Serializer):
    """
    Open 311 service list
    """
    definition = serializers.SerializerMethodField('get_definition')
    metadata = serializers.SerializerMethodField('get_metadata')
    keywords = serializers.SerializerMethodField('get_keywords')
    group = serializers.SerializerMethodField('get_group')
    type = serializers.SerializerMethodField('get_type')
    service_code = serializers.SerializerMethodField('get_service_code')
    service_name = serializers.SerializerMethodField('get_service_name')
    service_description = serializers.SerializerMethodField('get_service_description')
    
    def __init__(self, *args, **kwargs):
        self.service_type = kwargs.pop('service_type')
        super(ServiceListSerializer, self).__init__(*args, **kwargs)
    
    def get_definition(self, obj):
        request = self.context['request']
        format = self.context['format']
        return reverse('api_service_definition',
                       args=[self.service_type],
                       request=request,
                       format=format) 
    
    def get_service_code(self, obj):        
        return self.service_type
    
    def get_service_name(self, obj):        
        return SERVICES[self.service_type]['name']
    
    def get_service_description(self, obj):        
        return SERVICES[self.service_type]['description']
    
    def get_keywords(self, obj):        
        return SERVICES[self.service_type]['keywords']
    
    def get_group(self,obj):
        return SERVICES[self.service_type]['group']
    
    def get_metadata(self,obj):
        """ Open311 metadata indicates whether there are custom attributes """
        return 'true'
    
    def get_type(self,obj):
        """ type setting - TODO explain """
        return settings.NODESHOT['OPEN311']['TYPE']
    
    class Meta:
        fields= (
            'service_code',
            'service_name',
            'service_description',
            'keywords',
            'group',
            'definition',
            'metadata',
            'type',
        )


class ServiceNodeSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField('get_service_code')    
    attributes= serializers.SerializerMethodField('get_attributes')
    
    def get_service_code(self, obj):        
        return 'node'
    
    def create_attributes(self,attribute):
        return {
            "description": "%s" % attribute.description,
            "code": "%s" % attribute.code,
            "variable":True,
            "datatype":"%s" % attribute.datatype,
            "required": attribute.required,
            "datatype_description":"%s" % attribute.datatype_description,
            "order": "%s" % attribute.order,
            "values" :  attribute.values,
        }

    
    def get_attributes(self,obj):        
        attributes = []
        
        # Layer
        node_layer_attributes = Attribute(
                                    code='layer',
                                    description='Node layer',
                                    datatype='string',
                                    datatype_description='Layer for the node',
                                    order=1,
                                    required=True
                                )
        new_attribute=self.create_attributes(node_layer_attributes)
        attributes.append(new_attribute)
        
        # Name
        node_name_attributes = Attribute(
                                    code='name',
                                    description='Node name',
                                    datatype='string',
                                    datatype_description='Name for the node',
                                    order=2,
                                    required=True
                                )
        new_attribute=self.create_attributes(node_name_attributes)
        attributes.append(new_attribute)
        
        # Lat
        node_lat_attributes=Attribute(
                                    code='lat',
                                    description='Node latitude',
                                    datatype='string',
                                    datatype_description='Latitude for node',
                                    order=3,
                                    required=True)
        new_attribute=self.create_attributes(node_lat_attributes)
        attributes.append(new_attribute)
        
        # Long
        node_long_attributes=Attribute(code='long',
                                    description='Node longitude',
                                    datatype='string',
                                    datatype_description='Longitude for node',
                                    order=4,
                                    required=True)
        new_attribute=self.create_attributes(node_long_attributes)
        attributes.append(new_attribute)
        
        # Address
        node_address_attributes = Attribute(code='address',
                                    description='Node address',
                                    datatype='string',
                                    datatype_description='Address for node',
                                    order=5,
                                    required=False)
        new_attribute=self.create_attributes(node_address_attributes)
        attributes.append(new_attribute)
        
        # Elevation
        node_elev_attributes = Attribute(code='elev',
                                    description='Node elevation',
                                    datatype='string',
                                    datatype_description='Elevation for the node',
                                    order=6,
                                    required=False)
        new_attribute=self.create_attributes(node_elev_attributes)
        attributes.append(new_attribute)
        
        # Description
        node_desc_attributes = Attribute(code='elev',
                                    description='Node elevation',
                                    datatype='string',
                                    datatype_description='Description for node',
                                    order=7,
                                    required=False)
        new_attribute=self.create_attributes(node_desc_attributes)
        attributes.append(new_attribute)
        
        return (attributes)
    
    class Meta:
        #model = Layer
        fields = ('service_code', 'attributes', )


class RequestListSerializer(serializers.ModelSerializer):
    """
    Open 311 service request list
    """
    #definition = serializers.HyperlinkedIdentityField(view_name='api_service_detail', slug_field='slug')
    #metadata = serializers.SerializerMethodField('get_metadata')
    #keywords = serializers.SerializerMethodField('get_keywords')
    #group = serializers.SerializerMethodField('get_group')
    #type = serializers.SerializerMethodField('get_type')
    #service_code = serializers.IntegerField(source='id')
    #service_name = serializers.CharField(source='name')
    
    #def get_keywords(self,obj):        
    #    extra_data=obj.data
    #    if  extra_data is not None:
    #        keywords=extra_data.get('keywords', "")
    #    else:
    #        keywords=""
    #    return keywords
    #
    #def get_group(self,obj):        
    #    extra_data=obj.data
    #    if  extra_data is not None:   
    #        group=extra_data.get('group', "")
    #    else:
    #        group=""
    #    return group
    #
    #def get_metadata(self,obj):
    #    metadata = settings.NODESHOT['OPEN311']['METADATA']
    #    return metadata
    #
    #def get_type(self,obj):
    #    type = settings.NODESHOT['OPEN311']['TYPE']
    #    return type
    
    
    class Meta:
        model = Node

        #fields= (
        #    'service_code', 'service_name', 'description', 'keywords','group',
        #    'definition', 'metadata','type',
        #)

