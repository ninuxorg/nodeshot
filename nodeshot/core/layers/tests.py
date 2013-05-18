"""
nodeshot.core.layers unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from nodeshot.core.layers.models import Layer


class LayerTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        'test_layers.json',
        'test_nodes.json'
    ]
    
    def setUp(self):
        z = Layer()
        z.name = 'test layer'
        z.time_zone = 'GMT+1'
        z.slug = 'test-layer'
        z.lat = '10'
        z.lng = '10'
        z.zoom = '12'
        z.organization = 'ninux.org'
        self.layer = z
    
    #def test_email_filled(self):
    #    """ *** Either an email or some mantainers should be set *** """
    #    self.assertRaises(ValidationError, self.layer.full_clean)
    
    def test_parent_is_not_external(self):
        """ *** Layers cannot have parents which are flagged as "external" *** """
        self.layer.is_external = False
        self.layer.parent = Layer.objects.filter(is_external=True)[0]
        self.assertRaises(ValidationError, self.layer.full_clean)
