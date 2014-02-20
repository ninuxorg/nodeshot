import requests
import simplejson as json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from .base import BaseSynchronizer


class NodeshotMixin(object):
    """
    Nodeshot interoperability mixin
    """
    
    REQUIRED_CONFIG_KEYS = [
        'layer_url',
    ]
    
    def get_nodes(self, class_name, params):
        prefix = self.config['layer_url']
        suffix = 'nodes/' if 'geojson' not in class_name.lower() else 'nodes.geojson'
        # url from where to fetch nodes
        url = '%s%s' % (prefix, suffix)
        
        try:
            response = requests.get(url, params=params)
        except requests.exceptions.ConnectionError as e:
            return {
                'error': _('external layer not reachable'),
                'exception': list(e.message)
            }
        
        try:
            response.data = json.loads(response.content)
        except json.scanner.JSONDecodeError as e:
            return {
                'error': _('external layer is experiencing some issues because it returned invalid data'),
                'exception': list(e)
            }
        
        return response.data['nodes']


class Nodeshot(NodeshotMixin, BaseSynchronizer):
    """ Nodeshot interop test """
    pass