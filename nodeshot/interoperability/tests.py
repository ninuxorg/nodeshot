"""
nodeshot.core.layers unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from nodeshot.core.layers.models import Layer


class LayerTest(TestCase):
    
    fixtures = ['initial_data.json', 'test_users.json', 'test_layers.json', 'test_nodes.json']
    
    def setUp(self):
        pass
    
    #def test...
