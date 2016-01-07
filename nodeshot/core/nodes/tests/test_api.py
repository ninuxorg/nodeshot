"""
nodeshot.core.nodes unit tests
"""

import os
import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures

from ..models import Node, Image


class TestApi(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]

    IMAGE_FILE = '{0}/static/image_unit_test.gif'.format(os.path.dirname(os.path.realpath(__file__)))
    NODE_URL = reverse('api_node_details', args=['fusolab'])
    NODE_IMAGES_URL = reverse('api_node_images', args=['fusolab'])
    NODE_DATA = {
        "name": "fusolab",
        "user": "romano",
        "elev": 80.0,
        "address": "",
        "description": "Fusolab test 2",
        "access_level": "public",
        "layer": "rome",
        "geometry": json.loads(GEOSGeometry("POINT (12.582239191899999 41.872041927700003)").json)
    }

    def test_node_list(self):
        url = reverse('api_node_list')
        response = self.client.get(url)
        public_node_count = Node.objects.published().access_level_up_to('public').count()
        self.assertEqual(public_node_count, len(response.data['results']))

    def test_node_creation(self):
        url = reverse('api_node_list')
        node = {
            "layer": "rome",
            "name": "test distance",
            "address": "via dei test",
            "description": "",
            "geometry": json.loads(GEOSGeometry("POINT (12.99 41.8720419277)").json),
        }
        # POST: 403 - unauthenticated
        response = self.client.post(url, json.dumps(node), content_type='application/json')
        self.assertEqual(403, response.status_code)
        # POST: 201
        self.client.login(username='registered', password='tester')
        response = self.client.post(url, json.dumps(node), content_type='application/json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user'], 'registered')
        node = Node.objects.get(slug='test-distance')
        self.assertEqual(node.name, "test distance")

    def test_node_list_search(self):
        url = reverse('api_node_list')
        # GET: 200
        response = self.client.get(url, {"search": "Fusolab"})
        self.assertEqual(response.data['count'], 1)

    def test_node_list_filter_layers(self):
        url = reverse('api_node_list')
        response = self.client.get(url, {"layers": "rome"})
        self.assertEqual(response.data['count'], 4)
        response = self.client.get(url, {"layers": "viterbo"})
        self.assertEqual(response.data['count'], 2)
        response = self.client.get(url, {"layers": "rome,viterbo"})
        self.assertEqual(response.data['count'], 6)
        response = self.client.get(url, {"layers": "rome,viterbo,pisa"})
        self.assertEqual(response.data['count'], 8)

    def test_delete_node(self):
        node = Node.objects.first()
        node.delete()

    def test_node_geojson_list(self):
        """ test node geojson list """
        url = reverse('api_node_gejson_list')
        # GET: 200
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_node_geojson_list_filter_layers(self):
        url = reverse('api_node_gejson_list')
        response = self.client.get(url, {"layers": "rome"})
        self.assertEqual(len(response.data['features']), 4)
        response = self.client.get(url, {"layers": "viterbo"})
        self.assertEqual(len(response.data['features']), 2)
        response = self.client.get(url, {"layers": "rome,viterbo"})
        self.assertEqual(len(response.data['features']), 6)
        response = self.client.get(url, {"layers": "rome,viterbo,pisa"})
        self.assertEqual(len(response.data['features']), 8)

    def test_node_details(self):
        """ test node details """
        # GET: 200
        response = self.client.get(self.NODE_URL)
        self.assertEqual(200, response.status_code)
        node = response.data
        # images_url in node['images']
        self.assertTrue(isinstance(node['relationships']['images'], list))
        self.assertTrue(isinstance(node['relationships']['images'][0], dict))

    def test_node_details_403(self):
        """ test node details """
        # PUT: 403 - must be logged in
        response = self.client.put(self.NODE_URL)
        self.assertEqual(403, response.status_code)
        # PUT: 403 - only owner can edit
        self.client.login(username='pisano', password='tester')
        response = self.client.put(self.NODE_URL,
                                   json.dumps(self.NODE_DATA),
                                   content_type='application/json')
        self.assertEqual(403, response.status_code)

    def test_node_put(self):
        self.client.login(username='romano', password='tester')
        response = self.client.put(self.NODE_URL,
                                   json.dumps(self.NODE_DATA),
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        node = Node.objects.get(slug='fusolab')
        self.assertEqual(node.name, 'fusolab')
        self.assertEqual(node.description, 'Fusolab test 2')

    def test_node_patch(self):
        self.client.login(username='romano', password='tester')
        response = self.client.patch(self.NODE_URL,
                                     '{"description": "Patched Fusolab Desc"}',
                                     content_type='application/json')
        self.assertEqual(200, response.status_code)
        node = Node.objects.get(slug='fusolab')
        self.assertEqual(node.description, 'Patched Fusolab Desc')

    def test_node_acl(self):
        # CAN'T GET restricted if not authenticated
        fusolab = Node.objects.get(slug='fusolab')
        fusolab.access_level = 2
        fusolab.save()
        response = self.client.get(self.NODE_URL)
        self.assertEqual(404, response.status_code)
        # Admin can get it
        self.client.login(username='admin', password='tester')
        response = self.client.get(self.NODE_URL)
        self.assertEqual(200, response.status_code)

    def test_node_unpublished(self):
        # unpublished will return 404
        fusolab = Node.objects.get(slug='fusolab')
        fusolab.is_published = False
        fusolab.save()
        response = self.client.get(self.NODE_URL)
        self.assertEqual(404, response.status_code)

    def test_node_delete(self):
        self.client.login(username='admin', password='tester')
        response = self.client.delete(self.NODE_URL)
        self.assertEqual(204, response.status_code)
        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(slug='fusolab')

    def test_node_images_relationship(self):
        response = self.client.get(self.NODE_URL)
        self.assertEqual(200, response.status_code)
        images = response.data['relationships']['images']
        public_image_count = Image.objects.access_level_up_to('public').filter(node__slug='fusolab').count()
        self.assertEqual(public_image_count, len(images))
        # admin can get more images
        self.client.login(username='admin', password='tester')
        response = self.client.get(self.NODE_URL)
        images = response.data['relationships']['images']
        node_image_count = Image.objects.accessible_to(User.objects.get(pk=1)).filter(node__slug='fusolab').count()
        self.assertEqual(node_image_count, len(images))

    def test_node_images(self):
        response = self.client.get(self.NODE_IMAGES_URL)
        self.assertEqual(200, response.status_code)
        images = json.loads(response.content)
        public_image_count = Image.objects.access_level_up_to('public').filter(node__slug='fusolab').count()
        self.assertEqual(public_image_count, len(images))

    def test_node_images_admin(self):
        # admin can get more images
        self.client.login(username='admin', password='tester')
        response = self.client.get(self.NODE_IMAGES_URL)
        images = json.loads(response.content)
        node_image_count = Image.objects.accessible_to(User.objects.get(pk=1)).filter(node__slug='fusolab').count()
        self.assertEqual(node_image_count, len(images))

    def test_node_images_404(self):
        url = reverse('api_node_images', args=['idontexist'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_node_images_creation(self):
        self.client.login(username='admin', password='tester')
        good_post_data = {"description": "new image", "order": ""}
        bad_post_data = {"node": 100, "image": "jpeg99", "description": "new image", "order": ""}
        wrong_url = reverse('api_node_images', args=['idontexist'])
        # wrong slug -- 404
        response = self.client.post(wrong_url, good_post_data)
        self.assertEqual(response.status_code, 404)
        # correct POST data and correct slug -- 201
        with open(self.IMAGE_FILE, 'rb') as image_file:
            good_post_data['file'] = image_file
            response = self.client.post(self.NODE_IMAGES_URL, good_post_data)
            self.assertEqual(response.status_code, 201)
            # ensure image name is in DB
            image = Image.objects.all().order_by('-id')[0]
            self.assertIn('image_unit_test', image.file.name)
            self.assertIn('.gif', image.file.name)
            # remove file
            os.remove(image.file.file.name)
        # ensure additional post data "user" and "node" are ignored
        with open(self.IMAGE_FILE, 'rb') as image_file:
            bad_post_data['file'] = image_file
            response = self.client.post(self.NODE_IMAGES_URL, bad_post_data)
            self.assertEqual(response.status_code, 201)
            image_dict = json.loads(response.content)
            self.assertIn('fusolab', image_dict['details'])
            self.assertEqual(image_dict['description'], "new image")
            # ensure image name is in DB
            image = Image.objects.all().order_by('-id')[0]
            self.assertIn('image_unit_test', image.file.name)
            # remove file
            os.remove(image.file.file.name)

    def test_node_images_creation_403(self):
        good_post_data = {"description": "new image", "order": ""}
        self.client.login(username='pisano', password='tester')
        with open(self.IMAGE_FILE, 'rb') as image_file:
            good_post_data['file'] = image_file
            response = self.client.post(self.NODE_IMAGES_URL, good_post_data)
            self.assertEqual(response.status_code, 403)

    def test_node_image_list_permissions(self):
        # GET protected image should return 404
        url = reverse('api_node_images', args=['hidden-rome'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_node_can_edit(self):
        # cannot edit
        response = self.client.get(self.NODE_URL)
        self.assertFalse(response.data['can_edit'])
        # admin can edit
        self.client.login(username='admin', password='tester')
        response = self.client.get(self.NODE_URL)
        self.assertTrue(response.data['can_edit'])
        self.client.logout()
        # other user cannot edit
        self.client.login(username='registered', password='tester')
        response = self.client.get(self.NODE_URL)
        self.assertFalse(response.data['can_edit'])
        self.client.logout()
        # owner can edit
        self.client.login(username='romano', password='tester')
        response = self.client.get(self.NODE_URL)
        self.assertTrue(response.data['can_edit'])
        self.client.logout()
        # external node can't be edited
        Node.objects.create(**{
            'name': 'external',
            'slug': 'external',
            'layer_id': 4,
            'geometry': 'POINT (12.9732427 42.638304372)'
        })
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_details', args=['external'])
        response = self.client.get(url)
        self.assertFalse(response.data['can_edit'])
        response = self.client.patch(url, '{"name": "external 2"}', content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_node_geojson_list_pagination(self):
        # create a few nodes
        for n in range(0, 5):
            Node.objects.create(
                name='node-%d' % n,
                slug='node-%d' % n,
                layer_id=1,
                geometry='POINT (42.0454 12.%d45342)' % n
            )
        url = reverse('api_node_gejson_list')
        response = self.client.get(url)
        # ensure all results are returned by default
        count = Node.objects.published().access_level_up_to('public').count()
        self.assertEqual(len(response.data['features']), count)
        # ensure pagination doesn't break geojson format
        response = self.client.get(url, {'limit': '1'})
        self.assertIn('type', response.data)
        self.assertIn('features', response.data)
        self.assertEqual(len(response.data['features']), 1)

    def test_node_integrity_error_api(self):
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_list')
        json_data = json.dumps({
            "name": "pomezia",
            "slug": "",
            "layer": "rome",
            "geometry": {"type": "Point", "coordinates": [12.50094473361969, 41.66767450196442]},
            "elev": 0,
            "address": "",
            "description": ""
        })
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_elevation_api(self):
        url = reverse('api_elevation_profile')
        response = self.client.get(url, {
            'path': '41.8890404543067518,12.5253334454477372|41.8972185849048984,12.4902286938660296'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('LineString', response.data['geometry']['type'])
        self.assertEqual(len(response.data['geometry']['coordinates']), 72)
        self.assertEqual(len(response.data['geometry']['coordinates'][0]), 3)
        self.assertEqual(len(response.data['geometry']['coordinates'][-1]), 3)

    def test_elevation_api_none_path(self):
        """
        See #267
        https://github.com/ninuxorg/nodeshot/issues/267
        """
        url = reverse('api_elevation_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
