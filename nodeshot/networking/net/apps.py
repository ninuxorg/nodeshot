from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.networking.net'

    def ready(self):
        """ Add relationship to ExtensibleNodeSerializer """
        from nodeshot.core.nodes.base import ExtensibleNodeSerializer

        ExtensibleNodeSerializer.add_relationship(**{
            'name': 'devices',
            'view_name': 'api_node_devices',
            'lookup_field': 'slug'
        })
