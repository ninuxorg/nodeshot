from copy import copy

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework_gis import serializers as geoserializers

from .settings import ADDITIONAL_NODE_FIELDS
from .base import ExtensibleNodeSerializer
from .models import Node, Status, Image


__all__ = [
    'NodeListSerializer',
    'NodeSerializer',
    'NodeGeoJsonSerializer',
    'ImageSerializer',
    'ImageEditSerializer',
    'ImageRelationSerializer',
    'StatusSerializer'
]


class NodeSerializer(ExtensibleNodeSerializer):
    """ node detail """
    can_edit = serializers.SerializerMethodField()

    def get_can_edit(self, obj):
        """ returns true if user has permission to edit, false otherwise """
        view = self.context.get('view')
        request = copy(self.context.get('request'))
        request._method = 'PUT'
        try:
            view.check_object_permissions(request, obj)
        except (PermissionDenied, NotAuthenticated):
            return False
        else:
            return True

    def validate(self, attrs):
        # if instance hasn't been created yet
        if not self.instance:
            instance = self.Meta.model(**attrs)
            instance.full_clean()
            attrs['slug'] = instance.slug
        # if modifying an existing instance
        else:
            for key, value in attrs.items():
                setattr(self.instance, key, value)
            self.instance.full_clean()
            attrs['slug'] = self.instance.slug
        return attrs

    class Meta:
        model = Node
        fields = ['name', 'slug', 'status', 'user',
                  'access_level', 'layer', 'layer_name',
                  'geometry', 'elev', 'address',
                  'description'] + ADDITIONAL_NODE_FIELDS + \
                  ['added', 'updated', 'can_edit', 'relationships']
        read_only_fields = ('added', 'updated')
        geo_field = 'geometry'


class NodeListSerializer(NodeSerializer):
    """ node list """
    details = serializers.HyperlinkedIdentityField(view_name='api_node_details',
                                                   lookup_field='slug')

    class Meta:
        model = Node
        fields = ['name', 'slug', 'layer', 'layer_name',
                  'user', 'status', 'geometry', 'elev',
                  'address', 'description', 'updated',
                  'added', 'details']
        read_only_fields = ['added', 'updated']
        geo_field = 'geometry'
        id_field = 'slug'  # needed for NodeGeoJsonSerializer


class NodeGeoJsonSerializer(geoserializers.GeoFeatureModelSerializer,
                            NodeListSerializer):
    pass


class ImageSerializer(serializers.ModelSerializer):
    """ Serializer used to show list """
    order = serializers.IntegerField(default=0, allow_null=True)
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        """ returns uri of API image resource """
        args = {
            'slug': obj.node.slug,
            'pk': obj.pk
        }
        return reverse('api_node_image_detail',
                       kwargs=args,
                       request=self.context.get('request', None))

    class Meta:
        model = Image
        fields = ('id', 'file',
                  'description', 'order',
                  'access_level', 'added',
                  'updated', 'details')
        read_only_fields = ('added', 'updated')


class ImageEditSerializer(ImageSerializer):
    """ Serializer for image edit """
    class Meta:
        model = Image
        fields = ImageSerializer.Meta.fields
        read_only_fields = ('file', 'added', 'updated')


class ImageRelationSerializer(ImageSerializer):
    """ Serializer to reference images """
    class Meta:
        model = Image
        fields = ('id', 'file', 'description', 'added', 'updated')


ExtensibleNodeSerializer.add_relationship(
    'images',
    serializer=ImageRelationSerializer,
    many=True,
    queryset=lambda obj, request: obj.image_set.accessible_to(request.user).all()
)


# --------- Status --------- #


class StatusSerializer(serializers.ModelSerializer):
    """ status list """
    class Meta:
        model = Status
        fields = ['name', 'slug', 'description',
                  'fill_color', 'stroke_color',
                  'stroke_width', 'text_color',
                  'is_default']
