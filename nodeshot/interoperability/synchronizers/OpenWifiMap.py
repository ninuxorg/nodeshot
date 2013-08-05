import requests
import simplejson as json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from .base import BaseConverter


class OpenWifiMapMixin(object):
    """
    Having fun?
    """
    
    REQUIRED_CONFIG_KEYS = [
        'openwifimap_url',
    ]
    
    def __init__(self, *args, **kwargs):
        super(OpenWifiMapMixin, self).__init__(*args, **kwargs)
        
        # base url
        self.update_node_base_url = '%supdate_node' % self.config['openwifimap_url']
    
    def convert_format(self, node):
        return {
            "type": "node",
            "hostname": node.slug,
            "latitude": node.coords.coords[1],
            "longitude": node.coords.coords[0],
            "updateInterval": 6000
        }
    
    def add(self, node):
        """ add a new node into OpenWifiMap db """
        record = self.convert_format(node)
        
        api_url = '%s/%d' % (self.update_node_base_url, node.pk)
        
        # openwifimap sync
        response = requests.put(api_url, data=json.dumps(record),
                                headers={ 'content-type': 'application/json' })
        
        if response.status_code != 201:
            raise ImproperlyConfigured('Something went wrong while creating OpenWifiMap record with id %s: %s' % (node.pk, response.content))
        
        return True
    
    change = add


class OpenWifiMap(OpenWifiMapMixin, BaseConverter):
    """ OpenWifiMap test """
    pass