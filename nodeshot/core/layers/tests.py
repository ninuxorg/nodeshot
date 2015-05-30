"""
nodeshot.core.layers unit tests
"""

import simplejson as json

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.gis.geos import GEOSGeometry, Point

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
        self.assertEquals(published_layers_count, layers_count - 1)

        # external() method
        self.assertEquals(Layer.objects.external().count(), Layer.objects.filter(is_external=True).count())

        # mix external and published
        count = Layer.objects.filter(is_external=True, is_published=True).count()
        self.assertEquals(Layer.objects.external().published().count(), count)
        self.assertEquals(Layer.objects.published().external().count(), count)

    def test_layer_new_nodes_allowed(self):
        layer = Layer.objects.get(pk=1)
        layer.new_nodes_allowed = False
        layer.full_clean()
        layer.save()

        # ensure changing an existing node works
        node = layer.node_set.all()[0]
        node.name = 'changed'
        node.full_clean()
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

    def test_layer_nodes_minimum_distance(self):
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

        layer.nodes_minimum_distance = 100
        layer.save()

        try:
            new_node.full_clean()
        except ValidationError as e:
            self.assertIn(_('Distance between nodes cannot be less than %s meters') % layer.nodes_minimum_distance, e.messages)
            return

        self.assertTrue(False, 'validation not working as expected')

    def test_layers_api(self, *args, **kwargs):
        """
        Layers endpoint should be reachable and return 404 if layer is not found.
        """
        layer = Layer.objects.get(pk=1)
        layer_slug = layer.slug
        fake_layer_slug = "idontexist"

        # api_layer list
        response = self.client.get(reverse('api_layer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('"is_external": false', response.content)

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

    def test_layers_api_results(self, *args, **kwargs):
        """
        layers resources should return the expected number of objects
        """
        layer = Layer.objects.get(pk=1)
        layer_count = Layer.objects.all().count()
        layer_slug = layer.slug

        # api_layer list
        response = self.client.get(reverse('api_layer_list'))
        api_layer_count = len(response.data)
        self.assertEqual(api_layer_count, layer_count)

        # api_layer_nodes_list
        response = self.client.get(reverse('api_layer_nodes_list', args=[layer_slug]))
        layer_public_nodes_count = Node.objects.filter(layer=layer).published().access_level_up_to('public').count()
        self.assertEqual(response.data['count'], layer_public_nodes_count)
        self.assertEqual(len(response.data['results']), layer_public_nodes_count)

        # api_layer_nodes_geojson
        response = self.client.get(reverse('api_layer_nodes_geojson', args=[layer_slug]))
        self.assertEqual(len(response.data['features']), layer_public_nodes_count)

    def test_layers_api_post(self):
        layer_count = Layer.objects.all().count()
        # POST to create, 400
        self.client.login(username='registered', password='tester')
        data = {
            "name": "test",
            "slug": "test",
            "center": "POINT (38.1154075128999921 12.5107643007999929)",
            "area": "POINT (38.1154075128999921 12.5107643007999929)"
        }
        response = self.client.post(reverse('api_layer_list'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(layer_count, Layer.objects.all().count())

        # POST to create 200
        self.client.logout()
        self.client.login(username='admin', password='tester')
        response = self.client.post(reverse('api_layer_list'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Layer.objects.all().count(), layer_count + 1)

    def test_unpublish_layer_should_unpublish_nodes(self):
        layer = Layer.objects.first()
        layer.is_published = False
        layer.full_clean()
        layer.save()
        for node in layer.node_set.all():
            self.assertFalse(node.is_published)

        layer = Layer.objects.first()
        layer.is_published = True
        layer.full_clean()
        layer.save()
        for node in layer.node_set.all():
            self.assertTrue(node.is_published)

    def test_layer_area_point_or_polygon(self):
        layer = Layer.objects.get(slug='rome')
        layer.area = GEOSGeometry('LINESTRING (12.19 41.92, 12.58 42.17)')
        try:
            layer.full_clean()
        except ValidationError as e:
            self.assertIn('Polygon', str(e))
            self.assertIn('Point', str(e))
        else:
            self.fail('ValidationError not raised (Polygon/Point area check)')
        layer.area = GEOSGeometry('POINT (12.19 41.92)')
        layer.full_clean()

    def test_layer_area_contains_node_validation(self):
        """ ensure area validation works as expected """
        layer = Layer.objects.get(slug='rome')
        layer.area = GEOSGeometry('POLYGON ((12.19 41.92, 12.58 42.17, 12.82 41.86, 12.43 41.64, 12.43 41.65, 12.19 41.92))')
        layer.full_clean()
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
        else:
            self.fail('validation not working as expected')

        # if area is a point the contains check won't be done
        layer.area = GEOSGeometry('POINT (30.0 30.0)')
        layer.full_clean()
        layer.save()
        new_node.full_clean()

    def test_node_geometry_distance_and_area(self):
        """ test minimum distance check between nodes """
        self.client.login(username='admin', password='tester')

        url = reverse('api_node_list')

        json_data = {
            "layer": "rome",
            "name": "test_distance",
            "slug": "test_distance",
            "address": "via dei test",
            "description": "",
            "geometry": json.loads(GEOSGeometry("POINT (12.5822391919000012 41.8720419276999820)").json),
        }
        layer = Layer.objects.get(pk=1)
        layer.nodes_minimum_distance = 100
        layer.full_clean()
        layer.save()

        # Node coordinates don't respect minimum distance. Insert should fail because coords are near to already existing PoI ( fusolab )
        response = self.client.post(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(400, response.status_code)

        # Node coordinates respect minimum distance. Insert should succed
        json_data['geometry'] = json.loads(GEOSGeometry("POINT (12.7822391919 41.8720419277)").json)
        response = self.client.post(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(201, response.status_code)

        # Disable minimum distance control in layer and update node inserting coords too near. Insert should succed
        layer.nodes_minimum_distance = 0
        layer.save()
        json_data['geometry'] = json.loads(GEOSGeometry("POINT (12.5822391917 41.872042278)").json)
        n = Node.objects.get(slug='test_distance')
        node_slug = n.slug
        url = reverse('api_node_details', args=[node_slug])
        response = self.client.put(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(200, response.status_code)

        # re-enable minimum distance and update again with coords too near. Insert should fail
        layer.nodes_minimum_distance = 100
        layer.save()
        url = reverse('api_node_details', args=[node_slug])
        response = self.client.put(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(400, response.status_code)

        # Defining an area for the layer and testing if node is inside the area
        layer.area = GEOSGeometry('POLYGON ((12.19 41.92, 12.58 42.17, 12.82 41.86, 12.43 41.64, 12.43 41.65, 12.19 41.92))')
        layer.save()

        # Node update should fail because coords are outside layer area
        json_data['geometry'] = json.loads(GEOSGeometry("POINT (50 50)").json)
        url = reverse('api_node_details', args=[node_slug])
        response = self.client.put(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(400, response.status_code)

        # Node update should succeed because coords are inside layer area and respect minimum distance
        json_data['geometry'] = json.loads(GEOSGeometry("POINT (12.7822391919 41.8720419277)").json)
        url = reverse('api_node_details', args=[node_slug])
        response = self.client.put(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(200, response.status_code)

        # Node update should succeed because layer area is disabled
        layer.area = GEOSGeometry("POINT (12.7822391919 41.8720419277)")
        layer.save()
        json_data['geometry'] = json.loads(GEOSGeometry("POINT (50 50)").json)
        url = reverse('api_node_details', args=[node_slug])
        response = self.client.put(url, json.dumps(json_data), content_type='application/json')
        self.assertEqual(200, response.status_code)

        # re-enable minimum distance
        layer.nodes_minimum_distance = 100
        layer.save()

        # delete new nodes just added before
        n.delete()

    def test_layer_center(self):
        l = Layer.objects.first()
        self.assertIsInstance(l.center, Point)
        self.assertEqual(l.center, l.area)
        l.area = GEOSGeometry('POLYGON ((12.19 41.92, 12.58 42.17, 12.82 41.86, 12.43 41.64, 12.43 41.65, 12.19 41.92))')
        l.save()
        self.assertIsInstance(l.center, Point)
        self.assertNotEqual(l.center, l.area)
        l.area = None
        self.assertIsNone(l.center)

    def test_external_layer_nodes_geojson(self):
        """ test node geojson list """
        url = reverse('api_layer_nodes_geojson', args=['vienna'])
        # GET: 200
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_external_layer_nodes(self):
        """ test node geojson list """
        url = reverse('api_layer_nodes_list', args=['vienna'])
        # GET: 200
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_layer_nodes_geojson_pagination(self):
        url = reverse('api_layer_nodes_geojson', args=['rome'])
        # ensure all results returned by default
        response = self.client.get(url)
        count = Node.objects.filter(layer__slug='rome').published().access_level_up_to('public').count()
        self.assertEqual(len(response.data['features']), count)
        # ensure pagination doesn't break geojson format
        response = self.client.get(url, {'limit': '1'})
        self.assertIn('type', response.data)
        self.assertIn('features', response.data)
        self.assertEqual(len(response.data['features']), 1)
