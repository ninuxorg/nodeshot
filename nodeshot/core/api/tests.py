from django.test import TestCase
from django.core.urlresolvers import reverse


class ApiTest(TestCase):
    fixtures = [
        'initial_data.json',
    ]

    def test_root_endpoint(self):
        """
        Root endpoint should be reachable
        """
        response = self.client.get(reverse('api_root_endpoint'))
        self.assertEqual(response.status_code, 200)
