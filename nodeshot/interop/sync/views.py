from django.contrib.admin.sites import site
from nodeshot.core.layers.models import Layer

from .models import LayerExternal
from .admin import LayerAdmin


def layer_external_reload_schema(request, pk):
    # if POST and synchronizer_path param
    if request.method == 'POST' and request.POST.get('synchronizer_path'):
        layer = Layer.objects.get(pk=pk)
        # get external layer or init a new one
        try:
            external = layer.external
        except LayerExternal.DoesNotExist:
            external = LayerExternal(layer=layer)
        # reset schema
        external.synchronizer_path = 'None'
        external._reload_schema()
        # set synchronizer_path
        external.synchronizer_path = request.POST.get('synchronizer_path')
        external.save()
        # pass a GET request to the admin view
        request.method = 'GET'
    # return layer admin change view instance
    return LayerAdmin(Layer, site).change_view(request, pk)
