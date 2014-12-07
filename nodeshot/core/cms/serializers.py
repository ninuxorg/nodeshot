from rest_framework import serializers

from .models import *


__all__ = [
    'PageListSerializer',
    'PageDetailSerializer',
    'MenuSerializer'
]


class PageListSerializer(serializers.ModelSerializer):
    """
    Page List Serializer
    """
    details = serializers.HyperlinkedIdentityField(view_name='api_page_detail', lookup_field='slug')

    class Meta:
        model = Page
        fields = ('title', 'slug', 'added', 'updated', 'details')


class PageDetailSerializer(PageListSerializer):
    """
    Page Detail Serializer
    """
    class Meta:
        model = Page
        fields = ('title', 'slug', 'content',
                  'meta_description', 'meta_keywords', 'meta_robots',
                  'added', 'updated', 'details')


class ChildrenSerializer(serializers.ModelSerializer):
    """
    Children Serializer
    """
    class Meta:
        model = MenuItem
        fields = ('name', 'url', 'classes')


class MenuSerializer(serializers.ModelSerializer):
    """
    Menu Serializer
    """
    children = serializers.SerializerMethodField('get_children')

    def get_children(self, obj):
        user = self.context['request'].user
        queryset = obj.menuitem_set.published().accessible_to(user)
        return ChildrenSerializer(queryset, many=True).data

    class Meta:
        model = MenuItem
        fields = ('name', 'url', 'classes', 'children')
