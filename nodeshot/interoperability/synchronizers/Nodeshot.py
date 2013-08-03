import requests
import simplejson as json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from .base import BaseConverter


class NodeshotMixin(object):
    """
    Nodeshot interoperability mixin
    """
    
    REQUIRED_CONFIG_KEYS = [
        'layer_url',
    ]
    
    def __init__(self, *args, **kwargs):
        super(NodeshotMixin, self).__init__(*args, **kwargs)
        
        # base url
        self.nodes_url = '%snodes/' % self.config['layer_url']
    
    def get_nodes(self):
        try:
            response = requests.get(self.nodes_url)
            response.data = json.loads(response.content)
            return response.data['nodes']
        except requests.exceptions.ConnectionError as e:
            return { 'error': list(e.message) }


class Nodeshot(NodeshotMixin, BaseConverter):
    """ Nodeshot interop test """
    pass