import simplejson as json
from django.core.urlresolvers import reverse
from nodeshot.core.base.tests import BaseTestCase, user_fixtures


class DefaultUiTest(BaseTestCase):

    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]

    def test_index(self):
        response = self.client.get(reverse('ui:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_essential_data(self):
        response = self.client.get(reverse('api_ui_essential_data'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('layers', response.data)
        self.assertIn('nodes', response.data)
        self.assertIn('status', response.data)
        self.assertIn('menu', response.data)
