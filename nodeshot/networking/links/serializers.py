from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from nodeshot.core.base.serializers import DynamicRelationshipsMixin

from .models import *


__all__ = [
    'LinkListSerializer',
    'LinkDetailSerializer',
    'LinkListGeoJSONSerializer',
    'LinkDetailGeoJSONSerializer',
    'PaginatedLinkSerializer',
]


class LinkListSerializer(gis_serializers.GeoModelSerializer):
    """ location serializer  """
    layer = serializers.Field('layer_slug')
    quality = serializers.Field(source='quality')
    status = serializers.Field(source='get_status_display')
    type = serializers.Field(source='get_type_display')
    node_a_name = serializers.Field(source='node_a_name')
    node_b_name = serializers.Field(source='node_b_name')

    class Meta:
        model = Link
        fields = [
            'id',
            'layer',
            'node_a_name', 'node_b_name',
            'status', 'type', 'line',
            'metric_type', 'metric_value',
        ]


class LinkListGeoJSONSerializer(LinkListSerializer, gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'line'
        fields = LinkListSerializer.Meta.fields[:]


class LinkDetailSerializer(DynamicRelationshipsMixin, LinkListSerializer):
    interface_a_mac = serializers.Field(source='interface_a_mac')
    interface_b_mac = serializers.Field(source='interface_b_mac')
    relationships = serializers.SerializerMethodField('get_relationships')

    # this is needed to avoid adding stuff to DynamicRelationshipsMixin
    _relationships = {}

    class Meta:
        model = Link
        fields = [
            'id',
            'layer',
            'node_a_name', 'node_b_name',
            'interface_a_mac', 'interface_b_mac',
            'status', 'type', 'line',
            'quality', 'metric_type', 'metric_value',
            'max_rate', 'min_rate', 'dbm', 'noise',
            'first_seen', 'last_seen',
            'added', 'updated', 'relationships'
        ]

LinkDetailSerializer.add_relationship(
    'node_a',
    view_name='api_node_details',
    lookup_field='node_a_slug'
)

LinkDetailSerializer.add_relationship(
    'node_b',
    view_name='api_node_details',
    lookup_field='node_b_slug'
)


class LinkDetailGeoJSONSerializer(LinkDetailSerializer, gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'line'
        fields = LinkDetailSerializer.Meta.fields[:]


class PaginatedLinkSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = LinkListSerializer
