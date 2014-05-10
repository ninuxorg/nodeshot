"""
nodeshot.core.layers unit tests
"""

import simplejson as json

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.gis.geos import GEOSGeometry

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node  # test additional validation added by layer model

from .models import Layer


class LayerTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
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
            'geometry': 'POINT (10.4389188797003565 43.7200020000987328)'
        })
        with self.assertRaises(ValidationError):
            node.full_clean()
        
        try:
            node.full_clean()
            assert()
        except ValidationError as e:
            self.assertIn(_('New nodes are not allowed for this layer'), e.messages)
    
    def test_layer_minimum_distance(self):
        """ ensure minimum distance settings works as expected """
        layer = Layer.objects.get(slug='rome')
        node = layer.node_set.all()[0]
        
        # creating node with same coordinates should not be an issue
        new_node = Node(**{
            'name': 'new_node',
            'slug': 'new_node',
            'layer': layer,
            'geometry': node.geometry
        })
        new_node.full_clean()
        new_node.save()
        
        layer.minimum_distance = 100
        layer.save()
        
        try:
            new_node.full_clean()
        except ValidationError as e:
            self.assertIn(_('Distance between nodes cannot be less than %s meters') % layer.minimum_distance, e.messages)
            return
        
        self.assertTrue(False, 'validation not working as expected')
    
    def test_layer_area_validation(self):
        """ ensure area validation works as expected """
        layer = Layer.objects.get(slug='rome')
        layer.area = GEOSGeometry('POLYGON ((12.19 41.92, 12.58 42.17, 12.82 41.86, 12.43 41.64, 12.43 41.65, 12.19 41.92))')
        layer.save()
        
        # creating node with same coordinates should not be an issue
        new_node = Node(**{
            'name': 'new_node',
            'slug': 'new_node',
            'layer': layer,
            'geometry': 'POINT (50.0 50.0)'
        })
        
        try:
            new_node.full_clean()
        except ValidationError as e:
            self.assertIn(_('Node must be inside layer area'), e.messages)
            return
        
        self.assertTrue(False, 'validation not working as expected')
    
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
        response = self.client.get(reverse('api_layer_detail', args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_detail', args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
        # api_layer_nodes
        response = self.client.get(reverse('api_layer_nodes_list', args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_nodes_list', args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
        # api_layer_nodes_geojson
        response = self.client.get(reverse('api_layer_nodes_geojson', args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_nodes_geojson', args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
    def test_layers_api_results(self,*args,**kwargs):
        """
        layers resources should return the expected number of objects
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
        response = self.client.get(reverse('api_layer_nodes_list', args=[layer_slug]))
        layer_public_nodes_count = Node.objects.filter(layer=layer).published().access_level_up_to('public').count()
        self.assertEqual(len(response.data['nodes']['results']), layer_public_nodes_count)
        
        # ensure number of elements is the expected, even by disabling layerinfo and pagination
        response = self.client.get(reverse('api_layer_nodes_list', args=[layer_slug]), { 'limit': 0, 'layerinfo': 'false' })
        self.assertEqual(len(response.data), layer_public_nodes_count)
        
        # api_layer_nodes_geojson
        response = self.client.get(reverse('api_layer_nodes_geojson', args=[layer_slug]), { 'limit': 0, 'layerinfo': 'true' })
        # each of 'features' values in geojson is a node
        self.assertEqual(len(response.data['nodes']['features']), layer_public_nodes_count)
        
        # test layer info geojson without layerinfo
        response = self.client.get(reverse('api_layer_nodes_geojson', args=[layer_slug]), { 'limit': 0 })
        # ensure "features" are at root level
        self.assertEqual(len(response.data['features']), layer_public_nodes_count)
        
    def test_layers_api_post(self):
        layer_count = Layer.objects.all().count()
        
        # POST to create, 400
        self.client.login(username='registered', password='tester')
        data = {
            "name": "test",
            "slug": "test", 
            "center": "POINT (38.1154075128999921 12.5107643007999929)", 
            "area": None
        }
        response = self.client.post(reverse('api_layer_list'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(layer_count, Layer.objects.all().count())
        
        # POST to create 200
        self.client.logout()
        self.client.login(username='admin', password='tester')
        response = self.client.post(reverse('api_layer_list'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(layer_count + 1, Layer.objects.all().count())
    
    def test_unpublish_layer_should_unpublish_nodes(self):
        layer = Layer.objects.first()
        layer.is_published = False
        layer.save()
        for node in layer.node_set.all():
            self.assertFalse(node.is_published)
        
        layer = Layer.objects.first()
        layer.is_published = True
        layer.save()
        for node in layer.node_set.all():
            self.assertTrue(node.is_published)
