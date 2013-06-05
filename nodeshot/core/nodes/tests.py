"""
nodeshot.core.nodes unit tests
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser

import simplejson as json

from .models import Node, Image


class ModelsTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        'test_layers.json',
        'test_nodes.json',
        'test_images.json'
    ]
    
    def test_current_status(self):
        """ test that node._current_status is none for new nodes """
        n = Node()
        self.failUnlessEqual(n._current_status, None, 'new node _current_status private attribute is different than None')
        #self.failUnlessEqual(n._current_hotspot, None, 'new node _current_status private attribute is different than None')
        n = Node.objects.all()[0]
        self.failUnlessEqual(n._current_status, n.status, 'new node _current_status private attribute is different than status')
        n.status = 2
        self.failIfEqual(n._current_status, n.status, 'new node _current_status private attribute is still equal to status')
        n.save()
        self.failUnlessEqual(n._current_status, n.status, 'new node _current_status private attribute is different than status')
        n.status = 3
        n.save()
    
    def test_node_manager(self):
        """ test manager methods of Node model """
        # published()
        Node.objects.published
        count = Node.objects.published().filter(layer=1).count()
        # no unplished nodes on that layer, so the count should be the same
        self.assertEqual(count, Node.objects.filter(layer=1).count())
        # unpublish the first
        node = Node.objects.published().filter(layer=1)[0]
        node.is_published = False
        node.save()
        # should be -1
        self.assertEqual(count-1, Node.objects.published().filter(layer=1).count())
        
        # Ensure GeoManager distance is available
        pnt = Node.objects.get(slug='pomezia').coords
        Node.objects.filter(coords__distance_lte=(pnt, 7000))
        
        # access level manager
        user = User.objects.get(pk=1, is_superuser=True)
        # superuser can see all nodes
        self.assertEqual(Node.objects.all().count(), Node.objects.accessible_to(user).count())
        # same but passing only user_id
        self.assertEqual(Node.objects.all().count(), Node.objects.accessible_to(user=1).count())
        # simulate non authenticated user
        self.assertEqual(8, Node.objects.accessible_to(AnonymousUser()).count())
        # public nodes
        self.assertEqual(8, Node.objects.access_level_up_to('public').count())
        # public and registered
        self.assertEqual(9, Node.objects.access_level_up_to('registered').count())
        # public, registered and community
        self.assertEqual(10, Node.objects.access_level_up_to('community').count())
        
        ### --- START CHAINING! WOOOO --- ###
        # 9 because we unpublished one
        self.assertEqual(9, Node.objects.published().access_level_up_to('community').count())
        self.assertEqual(9, Node.objects.access_level_up_to('community').published().count())
        # user 1 is admin and can see all the nodes, published() is the same as writing filter(is_published=True)
        count = Node.objects.all().filter(is_published=True).count()
        self.assertEqual(count, Node.objects.published().accessible_to(user=1).count())
        self.assertEqual(count, Node.objects.accessible_to(user=1).published().count())
        # chain with geographic query
        self.assertEqual(count, Node.objects.filter(coords__distance_lte=(pnt, 7000)).accessible_to(user=1).published().count())
        self.assertEqual(count, Node.objects.accessible_to(user=1).filter(coords__distance_lte=(pnt, 7000)).published().count())
        self.assertEqual(count, Node.objects.accessible_to(user=1).published().filter(coords__distance_lte=(pnt, 7000)).count())
        self.assertEqual(count, Node.objects.filter(coords__distance_lte=(pnt, 7000)).accessible_to(user=1).published().count())
    
    def test_image_manager(self):
        """ test manager methods of Image model """
        # admin can see all the images
        self.assertEqual(Image.objects.all().count(), Image.objects.accessible_to(user=1).count())


### ------ API tests ------ ###


class APITest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        'test_layers.json',
        'test_nodes.json',
        'test_images.json'
    ]
    
    #def setup(self):
    #    self.client.login(username='admin', password='tester')
    
    def test_node_list(self):
        """ test node list """
        url = reverse('api_node_list')
        
        # GET: 200
        response = self.client.get(url)
        nodes = json.loads(response.content)
        public_node_count = Node.objects.published().access_level_up_to('public').count()
        self.assertEqual(public_node_count, len(nodes))
        
        # POST
    
    def test_node_geojson_list(self):
        """ test node geojson list """
        url = reverse('api_node_gejson_list')
        
        # GET: 200
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
    
    def test_node_details(self):
        """ test node details """
        url = reverse('api_node_details', args=['fusolab'])
        
        # GET: 200
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        node = json.loads(response.content)
        images_url = reverse('api_node_images', args=['fusolab'])
        # images_url in node['images']
        self.assertIn(images_url, node['images'])
        
        # PUT
        
        # PATCH
        
        # CAN'T GET restricted if not authenticated
        fusolab = Node.objects.get(slug='fusolab')
        fusolab.access_level = 2
        fusolab.save()
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        
        # Admin can get it
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        # unpublished will return 404
        fusolab.is_published = False
        fusolab.save()
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
    
    def test_node_images(self):
        """ test node images """
        url = reverse('api_node_images', args=['fusolab'])
        
        # GET: 200
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        images = json.loads(response.content)
        public_image_count = Image.objects.access_level_up_to('public').filter(node__slug='fusolab').count()
        self.assertEqual(public_image_count, len(images))
        # admin can get more images
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        images = json.loads(response.content)
        node_image_count = Image.objects.accessible_to(1).filter(node__slug='fusolab').count()
        self.assertEqual(node_image_count, len(images))
        
        # GET: 404
        url = reverse('api_node_images', args=['idontexist'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        
        # POST
        # todo
    
    def test_node_coords_distance(self):
        json_data={
        "user": 1,
        "access_level": 0, 
        "name": "test_distance2", 
        "slug": "test_distance2", 
        "address": "via dei test", 
        "status": 0, 
        "is_published": True, 
        "layer": 1, 
        "coords": "POINT (12.4922005670872949 41.8904524119848318)", 
        "description": "", 
        "notes": ""
        }
        login=self.client.login(username='admin', password='tester')
        url = reverse('api_node_list')
        response = self.client.post(url,json_data)
        self.assertEqual(400, response.status_code)
