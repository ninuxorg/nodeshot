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
        # check wrong service in service_request
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':'not_exists'}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 404)
        
    def test_service_request_node(self):
        #service_request for nodes
        login = self.client.login(username='admin', password='tester')
        
        
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
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)        
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_node_incomplete(self):
        #POST requests
        
        #incorrect service_request for nodes
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
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 400)
    
    def test_service_request_vote(self):
        #service_request for votes
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"vote","node": 1,"vote":1}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_vote_incomplete(self):
        #incomplete service_request for votes
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"vote","vote":1}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_vote_incorrect(self):
        #incorrect service_request for votes
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"vote","node": 1,"vote":10}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_rating(self):
        #service_request for rating
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"rate","node": 1,"value":1}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_rating_incomplete(self):
        #incomplete service_request for rating
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"rate","value":1}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_rating_incorrect(self):
        #incorrect service_request for rating
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"rate","node": 1,"value":20}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        
        self.assertEqual(response.status_code, 400)
        
    def test_service_request_comment(self):
        #service_request for comments
        login = self.client.login(username='admin', password='tester')   
        service_request={'service_code':"comment","node": 1,"text":"OK"}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        
        self.assertEqual(response.status_code, 201)
        
    def test_service_request_comment_incomplete(self):
        #incomplete service_request for comments
        login = self.client.login(username='admin', password='tester')   
        #Vote
        service_request={'service_code':"comment","text":"OK"}
        url = "%s" % reverse('api_service_requests')
        response = self.client.post(url,service_request)
        
        self.assertEqual(response.status_code, 400)
        
    def test_get_service_request(self):
        #GET request detail 
        response = self.client.get(reverse('api_service_request', args=['node','1']))
        self.assertEqual(response.status_code, 200)
        #Wrong service code
        response = self.client.get(reverse('api_service_request', args=['wrong','1']))
        self.assertEqual(response.status_code, 404)
        #Not existing request
        response = self.client.get(reverse('api_service_request', args=['node','100']))
        self.assertEqual(response.status_code, 404)
        
    def test_get_service_requests(self):
        #GET requests list
        response = self.client.get(reverse('api_service_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        
        response = self.client.get(reverse('api_service_requests'),{'status':'open'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        
        response = self.client.get(reverse('api_service_requests'),{'status':'closed'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)
        
        response = self.client.get(reverse('api_service_requests'),{'status':'wrong'})
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(reverse('api_service_requests'),{'start_date':'wrong'})
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(reverse('api_service_requests'),{'start_date':'2013-01-01T17:57:02Z'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        
        response = self.client.get(reverse('api_service_requests'),{'start_date':'2013-01-01T17:57:02Z','end_date':'2013-04-01T17:57:02Z'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        
        response = self.client.get(reverse('api_service_requests'),{'start_date':'2015-01-01T17:57:02Z'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        
        
    
        
        
        