from rest_framework import serializers
from nodeshot.core.base.serializers import HyperlinkedField
from .models import *    # noqa


__all__ = [
    'UnreadNotificationSerializer',
    'NotificationSerializer',
    'EmailNotificationSettingsSerializer',
    'WebNotificationSettingsSerializer'
]


class UnreadNotificationSerializer(serializers.ModelSerializer):
    """
    Unread notification serializer
    """
    from_user_id = serializers.Field()
    from_user_detail = serializers.HyperlinkedRelatedField(source='from_user',
                                                           view_name='api_profile_detail',
                                                           read_only=True)
    related_object = serializers.SerializerMethodField()

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
    class Meta:
        model = Notification
        fields = ('id', 'type', 'is_read', 'from_user_id',
                  'from_user_detail', 'related_object',
                  'text', 'added')


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
