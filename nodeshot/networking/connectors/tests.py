"""
nodeshot.networking.connectors unit tests
"""

import simplejson as json

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures


class ConnectorTest(BaseTestCase):
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_routing_protocols.json',
        'test_devices.json',
        'test_interfaces.json',
        'test_ip_addresses.json'
    ]
    
    def setUp(self):
        pass
    
    def test_something(self):
        """ reminder """
        self.assertEquals(True, False)
    