from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, pagination
from rest_framework_gis import serializers as geoserializers
from nodeshot.core.base.serializers import DynamicRelationshipsMixin


class ExtensibleNodeSerializer(DynamicRelationshipsMixin, geoserializers.GeoModelSerializer):
    """ node detail """
    user = serializers.Field(source='user.username')
    status = serializers.Field(source='status.slug')
    geometry = geoserializers.GeometryField(label=_('coordinates'))
    layer_name = serializers.Field(source='layer.name')
    access_level = serializers.Field(source='get_access_level_display')
    relationships = serializers.SerializerMethodField('get_relationships')

