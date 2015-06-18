from swampdragon.serializers.model_serializer import ModelSerializer


class NotificationSerializer(ModelSerializer):
	class Meta:
		model = 'notifications.Notification'
		publish_fields = ['text']
