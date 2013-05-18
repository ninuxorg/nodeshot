"""
tests for nodeshot.core.nodes
"""

from django.test import TestCase
from django.test.client import Client
import simplejson
from models import Node


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
    
    def test_current_status_and_hotspot(self):
        """ test that node._current_status is none for new nodes """
        n = Node()
        self.failUnlessEqual(n._current_status, None, 'new node _current_status private attribute is different than None')
        self.failUnlessEqual(n._current_hotspot, None, 'new node _current_status private attribute is different than None')
        n = Node.objects.all()[0]
        self.failUnlessEqual(n._current_status, n.status, 'new node _current_status private attribute is different than status')
        n.status = 2
        self.failIfEqual(n._current_status, n.status, 'new node _current_status private attribute is still equal to status')
        n.save()
        self.failUnlessEqual(n._current_status, n.status, 'new node _current_status private attribute is different than status')
        n.status = 3
        n.save()
        # hotspot
        self.failUnlessEqual(n._current_hotspot, n.is_hotspot, 'new node _current_hotspot private attribute is different than is_hotspot')
        n.is_hotspot = False
        self.failIfEqual(n._current_hotspot, n.is_hotspot, 'should not be equal because just changed')
        n.save()
        self.failUnlessEqual(n._current_hotspot, n.is_hotspot, 'should be equal again')
        n.is_hotspot = True
        n.save()
    
    #def test_api_nodes_public(self):
    #    """ test nodes api index and count publicly accessible nodes """
    #    url = '/api/v1/nodes/?format=json'
    #    client = Client()
    #    response = client.get(url)
    #    self.failUnlessEqual(response.status_code, 200, 'nodes index unreachable: %s' % url)
    #    json = simplejson.loads(response.content)
    #    nodes = json.get('objects')
    #    # olny 8 publicly accessible nodes
    #    self.failUnlessEqual(len(nodes), 8, 'amount of public nodes mismatch')
    #
    #def test_api_nodes_layer_public(self):
    #    """ test nodes api nodes of a layer """
    #    url = '/api/v1/layers/rome/nodes/?format=json'
    #    client = Client()
    #    response = client.get(url)
    #    self.failUnlessEqual(response.status_code, 200, 'nodes index unreachable: %s' % url)
    #    json = simplejson.loads(response.content)
    #    nodes = json.get('objects')
    #    # olny 8 publicly accessible nodes
    #    self.failUnlessEqual(len(nodes), 4, 'amount of public nodes mismatch')
    #
    #def test_api_images_public(self):
    #    """ test image api index and count publicly accessible images """
    #    url = '/api/v1/images/?format=json'
    #    client = Client()
    #    response = client.get(url)
    #    self.failUnlessEqual(response.status_code, 200, 'images index unreachable: %s' % url)
    #    json = simplejson.loads(response.content)
    #    images = json.get('images')
    #    # olny 3 publicly accessible images
    #    self.failUnlessEqual(len(images), 3, 'amount of public images mismatch')
    #    # test "node" field is present
    #    node = images[0].get('node', False)
    #    self.failUnlessEqual(node, 'fusolab', 'unexpected value for "node" field of first image')
    #
    #def test_api_images_node_public(self):
    #    """ test nodes api images of a node """
    #    url = '/api/v1/nodes/fusolab/images/?format=json'
    #    client = Client()
    #    response = client.get(url)
    #    self.failUnlessEqual(response.status_code, 200, 'unreachable: %s' % url)
    #    json = simplejson.loads(response.content)
    #    images = json.get('images')
    #    # olny 8 publicly accessible nodes
    #    self.failUnlessEqual(len(images), 2, 'unexpected amount of public images of node "fusolab"')
