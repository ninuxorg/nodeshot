from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.interop.sync'

    def ready(self):
        """ patch LayerNodesList view to support external layers """
        from .models import LayerExternal
        from nodeshot.core.layers.views import LayerNodeListMixin

        def get_nodes(self, request, *args, **kwargs):
            try:
                external = self.layer.external
            except LayerExternal.DoesNotExist:
                external = False
            # override view get_nodes method if we have a custom one
            if external and self.layer.is_external and hasattr(external, 'get_nodes'):
                return external.get_nodes(self.__class__.__name__, request.query_params)
            # otherwise return the standard one
            else:
                return (self.list(request, *args, **kwargs)).data

        LayerNodeListMixin.get_nodes = get_nodes
