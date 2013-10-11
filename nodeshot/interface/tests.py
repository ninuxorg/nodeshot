"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import simplejson as json
from django.test import TestCase


class Open311Request(TestCase):
    def test_basic_addition(self):
        """
        open311 request
        """
        request = {"action" : "node_insert"}
        
        self.client.login(username='admin', password='tester')
        response = self.client.post(url, json.dumps(request), content_type='application/json')
        self.assertEqual('pippo', response.data)
