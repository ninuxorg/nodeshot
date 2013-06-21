"""
nodeshot.core.layers unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from nodeshot.core.layers.models import Layer
from nodeshot.core.base.tests import user_fixtures


class LayerTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_nodes.json'
    ]
    
    def setUp(self):
        pass
    
    #def test...
