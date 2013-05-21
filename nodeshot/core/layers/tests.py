"""
nodeshot.core.layers unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Layer


class LayerTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        'test_layers.json',
        'test_nodes.json'
    ]
    
    def setUp(self):
        pass
    
    def test_layer_manager(self):
        # published() method
        layers_count = Layer.objects.all().count()
        published_layers_count = Layer.objects.published().count()
        self.assertEquals(published_layers_count, layers_count)
        # after unpublishing one layer we should get 1 less layer in total
        l = Layer.objects.get(pk=1)
        l.is_published = False
        l.save()
        layers_count = Layer.objects.all().count()
        published_layers_count = Layer.objects.published().count()
        self.assertEquals(published_layers_count, layers_count-1)
        
        # external() method
        self.assertEquals(Layer.objects.external().count(), Layer.objects.filter(is_external=True).count())
        
