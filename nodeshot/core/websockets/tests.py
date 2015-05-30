from django.conf import settings

from nodeshot.core.base.tests import user_fixtures, BaseTestCase
from nodeshot.core.nodes.models import Node

from django.core import management


class TestWebsockets(BaseTestCase):
    """
    Test WebSockets
    """
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
    ]
    
    #def test_start_websocket_server(self):
    #    self.assertTrue(False, 'TODO')
