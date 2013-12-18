"""
nodeshot.open311.tests
"""

import simplejson as json
from django.core.urlresolvers import reverse

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