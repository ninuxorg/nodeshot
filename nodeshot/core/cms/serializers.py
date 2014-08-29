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
        fields = ('name', 'url', 'classes', 'added', 'updated')


class MenuSerializer(serializers.ModelSerializer):
    """
    Menu Serializer
    """
    children = serializers.SerializerMethodField('get_children')

    def get_children(self, obj):
        return ChildrenSerializer(obj.menuitem_set.published(), many=True).data

    class Meta:
        model = MenuItem
        fields = ('name', 'url', 'classes', 'added', 'updated', 'children')
