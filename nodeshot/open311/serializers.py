from django.conf import settings
import simplejson as json
from rest_framework import serializers, pagination
from rest_framework_gis import serializers as geoserializers

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.serializers import NodeListSerializer

from .base import Attribute

HSTORE_ENABLED = settings.NODESHOT['SETTINGS'].get('HSTORE', True)

if HSTORE_ENABLED:
    from nodeshot.core.base.fields import HStoreDictionaryField

__all__ = [
    'ServiceDetailSerializer',
    'ServiceListSerializer',
    'RequestListSerializer',
]

ACTIONS = ('node_insert','comment','voting','rating',)
RATING_CHOICES = [ {"key":n,"value":n} for n in range(1, 11) ]
VOTING_CHOICES = [ {"key":1,"value":1}, {"key":-1,"value":-1} ]


class ServiceListSerializer(serializers.ModelSerializer):
    """
    Open 311 service list
    """
    definition = serializers.HyperlinkedIdentityField(view_name='api_service_detail', slug_field='slug')
    metadata = serializers.SerializerMethodField('get_metadata')
    keywords = serializers.SerializerMethodField('get_keywords')
    group = serializers.SerializerMethodField('get_group')
    type = serializers.SerializerMethodField('get_type')
    service_code = serializers.IntegerField(source='id')
    service_name = serializers.CharField(source='name')
    
    def get_keywords(self, obj):        
        extra_data=obj.data
        if extra_data is not None:
            keywords=extra_data.get('keywords', "")
        else:
            keywords=""
        return keywords
    
    def get_group(self,obj):
        extra_data=obj.data
        if extra_data is not None:   
            group=extra_data.get('group', "")
        else:
            group=""
        return group
    
    def get_metadata(self,obj):
        """ metadata setting - TODO explain """
        return settings.NODESHOT['OPEN311']['METADATA']
    
    def get_type(self,obj):
        """ type setting - TODO explain """
        return settings.NODESHOT['OPEN311']['TYPE']
    
    class Meta:
        model = Layer

        fields= (
            'service_code', 'service_name', 'description',
            'keywords', 'group', 'definition',
            'metadata','type',
        )


class ServiceDetailSerializer(ServiceListSerializer):
    """
    Service details
    """
    service_code = serializers.IntegerField(source='id')
    attributes= serializers.SerializerMethodField('get_attributes')
    
    def create_attributes(self,attribute):
        return {
            "code": "%s" % attribute.code,
            "variable":True,
            "datatype":"%s" % attribute.datatype,
            "required": attribute.required,
            "datatype_description":"%s" % attribute.datatype_description,
            "order": "%s" % attribute.order,
            "description": "%s" % attribute.description,
            "values" :  attribute.values,
        }

    
    def get_attributes(self,obj):        
        layer=Layer.objects.get(pk=obj.id)
        attributes = []
        
        # Attributes to determine if node is already existing or has to be inserted
        insert_attributes=Attribute(code='action',description='Action to be taken ',\
                                    datatype='singlevaluelist',datatype_description=\
                                    'Specifies the kind of request: node insertion, comment, rating or vote',\
                                    order=1,required=True,values=ACTIONS)
        new_attribute=self.create_attributes(insert_attributes)
        attributes.append(new_attribute)
        
        # Attributes for node
        # Coordinates
        node_attributes=Attribute(code='node',description='Node identifier',\
                                    datatype='string',datatype_description=\
                                    'Coordinates in WKT format if node has to be inserted, node_id for actions on already existing node',order=2,required=True)
        new_attribute=self.create_attributes(node_attributes)
        attributes.append(new_attribute)
        
        # Name
        node_name_attributes = Attribute(code='node_name',description='Node name',\
                                    datatype='string',datatype_description='Name for the node. Required only for node insertion.',order=3,required=False)
        new_attribute=self.create_attributes(node_name_attributes)
        attributes.append(new_attribute)
        
        # Attributes for comments
        if layer.participation_settings.comments_allowed:
            comments_attributes = Attribute(code='comment_request',description='Comment request',\
                                            datatype='string',datatype_description='Comment',order=4) 
            new_attribute=self.create_attributes(comments_attributes)   
            attributes.append(new_attribute)
            
        # Attributes for voting   
        if layer.participation_settings.voting_allowed:
            voting_attributes = Attribute(
                                    code='vote_request',description='Vote request',
                                    datatype='singlevaluelist',
                                    datatype_description='Vote 1 or -1 ( Yes/No)',
                                    order=5,
                                    values=VOTING_CHOICES
                                ) 
            new_attribute=self.create_attributes(voting_attributes)   
            attributes.append(new_attribute)
            
        # Attributes for rating
        if layer.participation_settings.rating_allowed:
            rating_attributes = Attribute(code='rating_request',description='rating request',\
                                            datatype='singlevaluelist',datatype_description='Rating from 1 to 10',order=6\
                                            ,values=RATING_CHOICES) 
            new_attribute=self.create_attributes(rating_attributes)   
            attributes.append(new_attribute)
        return (attributes)
    
    class Meta:
        model = Layer
        fields = ('service_code', 'attributes')


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

