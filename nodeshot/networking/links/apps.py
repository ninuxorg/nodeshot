from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.networking.links'

    def ready(self):
        """ Add relationship to ExtensibleNodeSerializer """
        from nodeshot.core.nodes.base import ExtensibleNodeSerializer

        ExtensibleNodeSerializer.add_relationship(**{
            'name': 'links',
            'view_name': 'api_node_links',
            'lookup_field': 'slug'
        })
