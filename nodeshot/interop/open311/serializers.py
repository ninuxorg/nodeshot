from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeshot.core.base.serializers import ModelValidationSerializer
from nodeshot.core.nodes.models import Node, Image
from nodeshot.community.participation.models import Vote, Comment, Rating

from .base import SERVICES
from .settings import settings, TYPE, STATUS


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
    'NodeRequestListSerializer',
    'VoteRequestListSerializer',
    'CommentRequestListSerializer',
    'RatingRequestListSerializer',
]

RATING_CHOICES = [n for n in range(1, 11)]
VOTING_CHOICES = [-1, 1]


class ServiceListSerializer(serializers.Serializer):
    """
    Open 311 service list
    """
    definition = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    service_code = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.service_type = kwargs.pop('service_type','node')
        super(ServiceListSerializer, self).__init__(*args, **kwargs)

    def get_definition(self, obj):
        request = self.context['request']
        format = self.context['format']
        return reverse('api_service_definition_detail',
                       args=[self.service_type],
                       request=request,
                       format=format)

    def get_service_code(self, obj):
        return self.service_type

    def get_service_name(self, obj):
        return SERVICES[self.service_type]['name']

    def get_description(self, obj):
        return SERVICES[self.service_type]['description']

    def get_keywords(self, obj):
        return SERVICES[self.service_type]['keywords']

    def get_group(self,obj):
        return SERVICES[self.service_type]['group']

    def get_metadata(self,obj):
        """ Open311 metadata indicates whether there are custom attributes """
        return 'true'

    def get_type(self,obj):
        """ type setting """
        return TYPE

    class Meta:
        fields= ('service_code', 'service_name',
                 'description', 'keywords',
                 'group', 'definition',
                 'metadata', 'type')


class ServiceNodeSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    def get_service_code(self, obj):
        return 'node'

    def get_attributes(self, obj):
        return [
            # layer
            {
                'code': 'layer',
                'description': _('layer_slug'),
                'datatype': 'string',
                'datatype_description': _('Specify the slug of the layer in which you want to insert the node'),
                'order': 1,
                'required': True,
                'variable' : True
            },

            # name
            {
                'code': 'name',
                'description': _('name'),
                'datatype': 'string',
                'datatype_description': _('Name of the node you want to insert'),
                'order': 2,
                'required': True,
                'variable' : True
            },

            # lat
            {
                'code': 'lat',
                'description': _('latitude'),
                'datatype': 'string',
                'datatype_description': _('Latitude of node'),
                'order': 3,
                'required': True,
                'variable' : True
            },

            # long
            {
                'code': 'long',
                'description': _('longitude'),
                'datatype': 'string',
                'datatype_description': _('Longitude of node'),
                'order': 4,
                'required': True,
                'variable' : True
            },

            # address
            {
                'code': 'address',
                'description': _('address'),
                'datatype': 'string',
                'datatype_description': _('Address of node'),
                'order': 5,
                'required': False,
                'variable' : True
            },

            # elev (elevation)
            {
                'code': 'elev',
                'description': _('elevation'),
                'datatype': 'string',
                'datatype_description': _('Elevation of node'),
                'order': 6,
                'required': False,
                'variable' : True
            },

            # description
            {
                'code': 'description',
                'description': _('description'),
                'datatype': 'string',
                'datatype_description': _('Description of node'),
                'order': 7,
                'required': False,
                'variable' : True
            },

            # images
            {
                'code': 'images',
                'description': _('images'),
                'datatype': 'string',
                'datatype_description': _('Images related to node. A client may POST multiple files as multipart/form-data.\
                                          Requests return the URL for this images via the image_url field'),
                'order': 8,
                'required': False,
                'variable' : True
            }
        ]

    class Meta:
        fields = ('service_code', 'attributes')


class ServiceVoteSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

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
                'required': True,
                'variable' : True

            },
            # vote
            {
                'code': 'vote',
                'description': _('vote on a node'),
                'datatype': 'string',
                'datatype_description': _('Vote 1 or -1 (Like/Dislike)'),
                'order': 2,
                'required': True,
                'variable' : True,
                'values' : [1,-1]
            },

        ]

    class Meta:
        fields = ('service_code', 'attributes')


class ServiceCommentSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

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
                'required': True,
                'variable' : True
            },

            # vote
            {
                'code': 'comment',
                'description': _('comment on a node'),
                'datatype': 'string',
                'datatype_description': _('text of the comment'),
                'order': 2,
                'required': True,
                'variable' : True

            },

        ]

    class Meta:
        fields = ('service_code', 'attributes')


class ServiceRatingSerializer(serializers.Serializer):
    """
    Service details
    """
    service_code = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

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
                'required': True,
                'variable' : True,
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
                'variable' : True,
                'values' : RATING_CHOICES
            },

        ]

    class Meta:
        fields = ('service_code', 'attributes')


class NodeRequestListSerializer(ModelValidationSerializer):
    """
    Open 311 node request
    """
    service_request_id = serializers.SerializerMethodField()
    layer = serializers.ReadOnlyField(source='layer.name')
    layer_slug = serializers.ReadOnlyField(source='layer.slug')
    details = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    requested_datetime = serializers.ReadOnlyField(source='added')
    updated_datetime = serializers.ReadOnlyField(source='updated')
    lat = serializers.SerializerMethodField()
    long = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True)
    service_code = serializers.SerializerMethodField()

    def get_image_urls(self, obj):
        image_url = []
        for image in Image.objects.filter(node=obj.id):
            media_url = settings.MEDIA_URL
            if not media_url.startswith('http'):
                request = self.context['request']
                media_url = '{0}://{1}{2}'.format(request.scheme, request.get_host(), media_url)
            image_url.append('{0}{1}'.format(media_url, image.file))
        return image_url if image_url else ""

    def get_service_code(self, obj):
        return self.context['request'].query_params['service_code']

    def get_lat(self, obj):
        return obj.point.coords[1]

    def get_long(self, obj):
        return obj.point.coords[0]

    # def get_layer_name(self, obj):
    #     if obj:
    #         return obj.layer
    #     return ""
    #
    # def get_layer_slug(self, obj):
    #     if obj is None:
    #         return ""
    #     layer_slug =  obj.layer.slug
    #     return layer_slug

    def get_service_request_id(self, obj):
        if obj is None:
            return ""
        service_request_id = 'node-%d' % obj.id
        return service_request_id

    def get_details(self, obj):
        if obj is None:
            return ""
        return reverse('api_service_request_detail',
                       args=['node', obj.id],
                       request=self.context['request'],
                       format=self.context['format'])

    class Meta:
        model = Node
        fields= ('service_request_id', 'slug', 'name',
                 'service_code', 'layer', 'layer_slug',
                 'status', 'geometry', 'name',
                 'description', 'requested_datetime',
                 'updated_datetime', 'image_urls', 'image',
                 'details', 'address', 'lat', 'long')
        read_only_fields = ('geometry', 'id', 'status',
                            'is_published', 'access_level',
                            'data','notes','user','added',
                            'updated', 'slug')


class NodeRequestDetailSerializer(NodeRequestListSerializer):
    """
    Open 311 node request
    """
    class Meta:
        model = Node
        fields= ('layer', 'layer_slug', 'slug',
                 'name', 'status', 'geometry',
                 'description', 'address',
                 'requested_datetime', 'updated_datetime',
                 'image_urls',)


class NodeRequestSerializer(ModelValidationSerializer):
    """
    Open 311 node request
    """
    class Meta:
        model = Node


class VoteRequestListSerializer(serializers.ModelSerializer):
    """
    Open 311 vote request
    """
    service_code = serializers.CharField()

    class Meta:
        model = Vote
        fields= ('service_code', 'node', 'vote',)


class VoteRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 vote request
    """
    class Meta:
        model = Vote


class CommentRequestListSerializer(serializers.ModelSerializer):
    """
    Open 311 comment request
    """
    service_code = serializers.CharField()
    class Meta:
        model = Comment
        fields= ('service_code', 'node', 'text',)


class CommentRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 comment request
    """
    class Meta:
        model = Comment


class RatingRequestListSerializer(serializers.ModelSerializer):
    """
    Open 311 rating request
    """
    service_code = serializers.CharField()

    class Meta:
        model = Rating
        fields= ('service_code', 'node', 'value',)


class RatingRequestSerializer(serializers.ModelSerializer):
    """
    Open 311 rating request
    """
    class Meta:
        model = Rating
