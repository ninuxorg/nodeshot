"""
tests for nodeshot.core.nodes
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
    
    #def setUp(self):
    #    pass
    
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


class APITest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        'test_layers.json',
        'test_nodes.json',
        'test_images.json'
    ]
    
    def setup(self):
        self.client.login(username='admin', password='tester')    
    
    def test_node_images(self):
        """ test API node images method """
        url = reverse('api_node_images', args=['fusolab'])
        
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        # should find 3 images (see fixtures)
        images = json.loads(response.content)
        self.assertEqual(3, len(images))
        
        # test 404
        url = reverse('api_node_images', args=['idontexist'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)