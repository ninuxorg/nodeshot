"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import simplejson as json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from nodeshot.core.base.tests import user_fixtures


class Open311Request(TestCase):
    
    fixtures = [
    'initial_data.json',
    user_fixtures,
    'test_layers.json',
    'test_status.json',
    'test_nodes.json',
    'test_images.json'
]
    
    def test_request(self):
        """
        open311 request
        """
        url = reverse('api_request_list')
        request = {"action" : "node_insert"}
        
        self.client.login(username='admin', password='tester')
        response = self.client.post(url, request, content_type='application/json')
        self.assertEqual('ok', response.data)
