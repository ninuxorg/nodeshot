from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer

from nodeshot.core.base.serializers import HyperlinkedField

from .models import *


__all__ = [
    'UnreadNotificationSerializer',
    'NotificationSerializer',
    'PaginatedNotificationSerializer',
    'EmailNotificationSettingsSerializer',
    'WebNotificationSettingsSerializer'
]


class UnreadNotificationSerializer(serializers.ModelSerializer):
    """
    Unread notification serializer
    """
    from_user_id = serializers.Field(source='from_user_id')
    from_user_detail = serializers.HyperlinkedRelatedField(
        source='from_user',
        view_name='api_profile_detail',
        read_only=True
    )
    related_object = serializers.SerializerMethodField('get_related_object')
    
    def get_related_object(self, obj):
        related = obj.related_object
        if related is not None:
            if hasattr(related, 'slug'):
                return related.slug
            else:
                return related.id
        return None
    
    class Meta:
        model = Notification
        fields = (
            'id', 'type', 'is_read', 'from_user_id',
            'from_user_detail', 'related_object',
            'text', 'added'
        )


class NotificationSerializer(UnreadNotificationSerializer):
    """
    Notification serializer
    """
    class Meta:
        model = Notification
        fields = (
            'id', 'type', 'is_read', 'from_user_id',
            'from_user_detail', 'related_object',
            'text', 'added'
        )


class PaginatedNotificationSerializer(PaginationSerializer):
    """
    Serializes page objects of notification querysets.
    """
    class Meta:
        object_serializer_class = NotificationSerializer


class EmailNotificationSettingsSerializer(serializers.ModelSerializer):
    """
    Email Notification Settings serializer
    """
    uri = HyperlinkedField(view_name='api_notification_email_settings')
    
    class Meta:
        model = UserEmailNotificationSettings
        exclude = ('id', 'user',)


class WebNotificationSettingsSerializer(serializers.ModelSerializer):
    """
    Web Notification Settings serializer
    """
    uri = HyperlinkedField(view_name='api_notification_email_settings')
    
    class Meta:
        model = UserWebNotificationSettings
        exclude = ('id', 'user',)
