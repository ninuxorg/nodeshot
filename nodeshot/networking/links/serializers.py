from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from nodeshot.core.base.serializers import DynamicRelationshipsMixin

from .models import Link


__all__ = [
    'LinkListSerializer',
    'LinkDetailSerializer',
    'LinkListGeoJSONSerializer',
    'LinkDetailGeoJSONSerializer',
]


class LinkListSerializer(serializers.ModelSerializer):
    layer = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    status = serializers.ReadOnlyField(source='get_status_display')
    type = serializers.ReadOnlyField(source='get_type_display')

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
    relationships = serializers.SerializerMethodField()

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


class LinkDetailGeoJSONSerializer(LinkDetailSerializer,
                                  gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'line'
        fields = LinkDetailSerializer.Meta.fields[:]
