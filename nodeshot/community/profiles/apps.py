from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.community.profiles'

    def ready(self):
        """ Add user info to ExtensibleNodeSerializer """
        from nodeshot.core.nodes.base import ExtensibleNodeSerializer
        from .serializers import ProfileRelationSerializer

        ExtensibleNodeSerializer.add_relationship(
            name='user',
            serializer=ProfileRelationSerializer,
            queryset=lambda obj, request: obj.user
        )
