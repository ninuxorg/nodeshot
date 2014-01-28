"""
nodeshot.open311.tests
"""

import simplejson as json
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import GEOSGeometry

from nodeshot.core.base.tests import BaseTestCase, user_fixtures
from nodeshot.open311.base import SERVICES

class Open311Request(BaseTestCase):
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]
    
    def test_service_list(self):
        response = self.client.get(reverse('api_service_list'))
        
        # ensure 4 services
        self.assertEqual(len(response.data), 4)
        
        # ensure these words are in response
        for word in SERVICES.keys():
            self.assertContains(response, word)
    
    def test_node_service_definition(self):
        response = self.client.get(reverse('api_service_definition', args=['node']))
        
        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'node')
        
        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 7)
        
    def test_vote_service_definition(self):
        response = self.client.get(reverse('api_service_definition', args=['vote']))
        
        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'vote')
        
        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 2)
    
    def test_comment_service_definition(self):
        response = self.client.get(reverse('api_service_definition', args=['comment']))
        
        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'comment')
        
        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 2)
    
    def test_rate_service_definition(self):
        response = self.client.get(reverse('api_service_definition', args=['rate']))
        
        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'rate')
        
        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 2)
        
    def test_service_request_wrong_service(self):
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':'not_exists'}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 404)
        
    def test_service_request_node(self):
        login = self.client.login(username='admin', password='tester')
        
        #Node
        service_request={
                        'service_code':"node",
                        "name": "montesacro4",
                        "slug": "montesacro4",
                        "layer": "rome",
                        "lat": "22.5253",
                        "lng": "41.8890",
                        "description": "test",
                        "geometry": "POINT (22.5253334454477372 41.8890404543067518)"
                        }
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_node_incomplete(self):
        login = self.client.login(username='admin', password='tester')
               
        service_request={
                        'service_code':"node",
                        "slug": "montesacro4",
                        "layer": "rome",
                        "lat": "22.5253",
                        "lng": "41.8890",
                        "description": "test",
                        "geometry": "POINT (22.5253334454477372 41.8890404543067518)"
                        }
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 400)
    
    def test_service_request_vote(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"vote","node": 1,"vote":1}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_vote_incomplete(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"vote","vote":1}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_vote_incorrect(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"vote","node": 1,"vote":10}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_rating(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"rate","node": 1,"value":1}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_rating_incomplete(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"rate","value":1}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_rating_incorrect(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"rate","node": 1,"value":20}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_comment(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"comment","node": 1,"text":"OK"}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_comment_incomplete(self):
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"comment","text":"OK"}
        url = "%s" % reverse('api_request_list')
        response = self.client.post(url,service_request)
        print response.content
        self.assertEqual(response.status_code, 400)
        
    
        
        
        