from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.core.layers'

    def ready(self):
        """ Add relationship to ExtensibleNodeSerializer """
        from nodeshot.core.nodes.serializers import ExtensibleNodeSerializer

        ExtensibleNodeSerializer.add_relationship(**{
            'name': 'layer',
            'view_name': 'api_layer_detail',
            'lookup_field': 'layer.slug'
        })
