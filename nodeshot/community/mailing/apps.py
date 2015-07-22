from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.community.mailing'

    def ready(self):
        """ Add relationship to ExtensibleNodeSerializer """
        from nodeshot.core.nodes.base import ExtensibleNodeSerializer

        ExtensibleNodeSerializer.add_relationship(**{
            'name': 'contact',
            'view_name': 'api_node_contact',
            'lookup_field': 'slug'
        })
