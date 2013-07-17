"""
nodeshot.core.layers unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node  # test additional validation added by layer model

from .models import Layer


class LayerTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_nodes.json'
    ]
    
    def setUp(self):
        pass
    
    def test_layer_manager(self):
        """ test Layer custom Manager """
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
        
        # mix external and published
        count = Layer.objects.filter(is_external=True, is_published=True).count()
        self.assertEquals(Layer.objects.external().published().count(), count)
        self.assertEquals(Layer.objects.published().external().count(), count)
    
    def test_layer_new_nodes_allowed(self):
        layer = Layer.objects.get(pk=1)
        layer.new_nodes_allowed = False
        layer.area = None
        layer.minimum_distance = 0
        layer.save()
        
        # ensure changing an existing node works
        node = layer.node_set.all()[0]
        node.name = 'changed'
        node.save()
        # re-get from DB, just to be sure
        node = Node.objects.get(pk=node.pk)
        self.assertEqual(node.name, 'changed')
        
        # ensure new node cannot be added
        node = Node(**{
            'name': 'test new node',
            'slug': 'test-new-node',
            'layer': layer,
            'coords': 'POINT (10.4389188797003565 43.7200020000987328)'
        })
        with self.assertRaises(ValidationError):
            node.full_clean()
        
        try:
            node.full_clean()
            assert()
        except ValidationError as e:
            self.assertIn(_('New nodes are not allowed for this layer'), e.messages)
    
    def test_layers_api(self,*args,**kwargs):
        """
        Layers endpoint should be reachable and return 404 if layer is not found.
        """
        layer = Layer.objects.get(pk=1)
        layer_slug = layer.slug
        fake_layer_slug = "idontexist"
        
        # api_layer list
        response = self.client.get(reverse('api_layer_list'))
        self.assertEqual(response.status_code, 200)
        
        # api's expecting slug in request,test with existing and fake slug
        # api_layer_detail
        response = self.client.get(reverse('api_layer_detail',args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_detail',args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
        # api_layer_nodes
        response = self.client.get(reverse('api_layer_nodes_list',args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_nodes_list',args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
        # api_layer_nodes_geojson
        response = self.client.get(reverse('api_layer_nodes_geojson',args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_nodes_geojson',args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
    def test_layers_api_results(self,*args,**kwargs):
        """
        Layers endpoint should return the expected number of objects
        """
        layer = Layer.objects.get(pk=1)
        layer_count = Layer.objects.all().count()
        layer_nodes = layer.node_set.count()
        layer_slug = layer.slug
        
        # api_layer list
        response = self.client.get(reverse('api_layer_list'))
        api_layer_count = len(response.data)
        self.assertEqual(api_layer_count, layer_count)
        
        # api_layer_nodes_list 
        response = self.client.get(reverse('api_layer_nodes_list',args=[layer_slug]))
        
        # each of 'node' values is a node
        api_layer_nodes = len(response.data['nodes'])
        self.assertEqual(api_layer_nodes, layer_nodes)
        
        # api_layer_nodes_geojson
        response = self.client.get(reverse('api_layer_nodes_geojson',args=[layer_slug]))
        
        # each of 'features' values in geojson is a node
        api_layer_nodes = len(response.data['features'])
        self.assertEqual(api_layer_nodes, layer_nodes)