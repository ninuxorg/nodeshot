"""
nodeshot.core.api unit tests
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured


class ParticipationModelsTest(TestCase):
    """ Models tests """
    
    fixtures = [
        'initial_data.json',
    ]
    
    def test_root_endpoint(self):
        """
        Root endpoint should be reachable
        """
        response = self.client.get(reverse('api_root_endpoint'))
        self.assertEqual(response.status_code, 200)