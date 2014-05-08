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
    
    details = serializers.HyperlinkedIdentityField(view_name='api_page_detail', slug_field='slug')
    
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


class MenuSerializer(serializers.ModelSerializer):
    """
    Menu Serializer
    """
    
    class Meta:
        model = MenuItem
        fields = ('name', 'url', 'added', 'updated')
