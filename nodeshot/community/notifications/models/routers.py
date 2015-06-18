from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter

from .models import Notification
from .serializers import NotificationSerializer


class NotificationRouter(ModelPubRouter):
	valid_verbs = ['subscribe']
	route_name = 'nodeshot-notifications'
	model = Notification
	serializer_class = NotificationSerializer


route_handler.register(NotificationRouter)
