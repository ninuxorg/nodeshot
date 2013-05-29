"""
nodeshot.core.api unit tests
"""

from django.test import TestCase
from django.core.urlresolvers import reverse


class ParticipationModelsTest(TestCase):
    """ Models tests """
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        #'test_layers.json',
        #'test_nodes.json',
        #'test_images.json'
    ]
    
    def test_root_endpoint(self):
        """
        Root endpoint should be reachable
        """
        response = self.client.get(reverse('api_root_endpoint'))
        self.assertEqual(response.status_code, 200)
