import simplejson as json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_gis import serializers as geoserializers

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Node, Image
from nodeshot.community.participation.models import Vote,Comment,Rating
from nodeshot.core.nodes.serializers import NodeListSerializer

from .base import SERVICES


__all__ = [
    'ServiceRatingSerializer',
    'ServiceCommentSerializer',
    'ServiceNodeSerializer',
    'ServiceVoteSerializer',
    'ServiceListSerializer',
    'NodeRequestSerializer',
    'VoteRequestSerializer',
    'CommentRequestSerializer',
    'RatingRequestSerializer',
    'NodeRequestDetailSerializer',
    'VoteRequestDetailSerializer',
    'CommentRequestDetailSerializer',
    'RatingRequestDetailSerializer',
    'NodeRequestListSerializer',
]

RATING_CHOICES = [ n for n in range(1, 11) ]
VOTING_CHOICES = [ -1, 1 ]


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
    attributes = serializers.SerializerMethodField('get_attributes')
    
    def get_service_code(self, obj):        
        return 'node'
    
    def get_attributes(self, obj):        
        return [
            # layer
            {
                'code': 'layer',
                'description': _('layer'),
                'datatype': 'string',
                'datatype_description': _('Specify in which layer you want to insert the node'),
                'order': 1,
                'required': True
            },
            
            # name
            {
                'code': 'name',
                'description': _('name'),
                'datatype': 'string',
                'datatype_description': _('Name of the node you want to insert'),
                'order': 2,
                'required': True
            },
            
            # lat
            {
                'code': 'lat',
                'description': _('latitude'),
                'datatype': 'string',
                'datatype_description': _('Latitude of node'),
                'order': 3,
                'required': True
            },
            
            # long
            {
                'code': 'long',
                'description': _('longitude'),
                'datatype': 'string',
                'datatype_description': _('Longitude of node'),
                'order': 4,
                'required': True
            },
            
            # address
            {
                'code': 'address',
                'description': _('address'),
                'datatype': 'string',
                'datatype_description': _('Address of node'),
                'order': 5,
                'required': False
            },
            
            # elev (elevation)
            {
                'code': 'elev',
                'description': _('elevation'),
                'datatype': 'string',
                'datatype_description': _('Elevation of node'),
                'order': 6,
                'required': False
            },
            
            # description
            {
                'code': 'description',
                'description': _('description'),
                'datatype': 'string',
                'datatype_description': _('Description of node'),
                'order': 7,
                'required': False
            },
            
            # images
            {
                'code': 'images',
                'description': _('images'),
                'datatype': 'string',
                'datatype_description': _('Images related to node. A client may POST multiple files as multipart/form-data. Requests return the URL for this images via the image_url field\
                                          '),
                'order': 8,
                'required': False
            }
        ]
    
    class Meta:
        fields = ('service_code', 'attributes')


class ServiceVoteSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField('get_service_code')    
    attributes = serializers.SerializerMethodField('get_attributes')
    
    def get_service_code(self, obj):        
        return 'vote'
    
    def get_attributes(self, obj):        
        return [
            # node_id
            {
                'code': 'node_id',
                'description': _('Node id'),
                'datatype': 'string',
                'datatype_description': _('Specify for which node you want to insert the vote'),
                'order': 1,
                'required': True
            },
            
            # vote
            {
                'code': 'vote',
                'description': _('vote on a node'),
                'datatype': 'string',
                'datatype_description': _('Vote 1 or -1 (Like/Dislike)'),
                'order': 2,
                'required': True,
                'values' : [1,-1]
            },

        ]
    
    class Meta:
        fields = ('service_code', 'attributes')


class ServiceCommentSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField('get_service_code')    
    attributes = serializers.SerializerMethodField('get_attributes')
    
    def get_service_code(self, obj):        
        return 'comment'
    
    def get_attributes(self, obj):        
        return [
            # node_id
            {
                'code': 'node_id',
                'description': _('Node id'),
                'datatype': 'string',
                'datatype_description': _('Specify for which node you want to insert the comment'),
                'order': 1,
                'required': True
            },
            
            # vote
            {
                'code': 'comment',
                'description': _('comment on a node'),
                'datatype': 'string',
                'datatype_description': _('text of the comment'),
                'order': 2,
                'required': True,
            },

        ]
    
    class Meta:
        fields = ('service_code', 'attributes')


class ServiceRatingSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField('get_service_code')    
    attributes = serializers.SerializerMethodField('get_attributes')
    
    def get_service_code(self, obj):        
        return 'rate'
    
    def get_attributes(self, obj):        
        return [
            # node_id
            {
                'code': 'node_id',
                'description': _('Node id'),
                'datatype': 'string',
                'datatype_description': _('Specify which node you want to rate'),
                'order': 1,
                'required': True
            },
            
            # rating
            {
                'code': 'rating',
                'description': _('rating of a node'),
                'datatype': 'string',
                'datatype_description': _('rate node from 1 to 10'),
                'order': 2,
                'required': True,
                'values' : RATING_CHOICES
            },

        ]
    
    class Meta:
        fields = ('service_code', 'attributes') 


class NodeRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 node request 
    """
    
    class Meta:
        model = Node
        
        
class VoteRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 vote request 
    """
    
    class Meta:
        model = Vote
        
        
class CommentRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 comment request 
    """
    
    class Meta:
        model = Comment
        
        
class RatingRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 rating request 
    """
    
    class Meta:
        model = Rating
        
        
class VoteRequestDetailSerializer(serializers.ModelSerializer):
    """
    Open 311 vote request 
    """
    
    class Meta:
        model = Vote
        fields= ('added','updated')
        
        
class CommentRequestDetailSerializer(serializers.ModelSerializer):
    """
    Open 311 comment request 
    """
    
    class Meta:
        model = Comment
        fields= ('added','updated')
        
class RatingRequestDetailSerializer(serializers.ModelSerializer):
    """
    Open 311 rating request 
    """
    
    class Meta:
        model = Rating
        fields= ('added','updated')
        

class NodeRequestListSerializer(serializers.ModelSerializer):
    """
    Open 311 node request 
    """  
    details = serializers.SerializerMethodField('get_details')
    image_urls = serializers.SerializerMethodField('get_image_urls')
    requested_datetime = serializers.Field(source='added')
    updated_datetime = serializers.Field(source='updated')
    #expired = serializers.Field(source='has_expired')
    
    def get_image_urls(self,obj):
        request = self.context['request']
        format = self.context['format']
        
        image_url =[]
        
        try:
            image = Image.objects.all().filter(node=obj.id)
        except:
            image=None
        
        if image is not None:
            for i in image:
                    image_url.append( '%s%s' % (settings.MEDIA_URL, i))
            return image_url
        else:
            return ""
    
    def get_details(self, obj):
        #self.get_serializer_context()
        request = self.context['request']
        format = self.context['format']
        
        return reverse('api_service_request',
                       args=['node',obj.id],
                       request=request,
                       format=format)
   
    class Meta:
        model = Node
        fields= ('status','geometry','description','address','requested_datetime','updated_datetime','image_urls','details',)
        
        

class NodeRequestDetailSerializer(NodeRequestListSerializer):
    """
    Open 311 node request 
    """  
   
    class Meta:
        model = Node
        fields= ('status','geometry','description','address','requested_datetime','updated_datetime', 'image_urls')
    



