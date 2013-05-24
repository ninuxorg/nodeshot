"""
tests for nodeshot.core.nodes
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

import simplejson as json

from .models import Node


class NodeTest(TestCase):
    
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


class NodeTest(TestCase):
    
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