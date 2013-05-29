"""
nodeshot.core.api unit tests
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings


class ParticipationModelsTest(TestCase):
    """ Models tests """
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        #'test_layers.json',
        #'test_nodes.json',
        #'test_images.json'
    ]
    
    def setUp(self):
       self.installed_apps = settings.INSTALLED_APPS
    
    def test_root_endpoint(self):
        """
        Root endpoint should be reachable
        """
        response = self.client.get(reverse('api_root_endpoint'))
        self.assertEqual(response.status_code, 200)
    
    def test_remove_one_from_installed_apps(self):
        """
        If removing one of the enabled API modules from installed apps the urls should not be listed in the endpoint
        """
        # remove participation from INSTALLED_APPS
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'nodeshot.community.participation']
        
        # ensure participation URLs is not there
        response = self.client.get(reverse('api_root_endpoint'))
        self.assertNotContains(response, 'participation')
        self.assertNotContains(response, 'comments')
        # ensure other URLs are still there
        self.assertContains(response, 'nodes')
    
