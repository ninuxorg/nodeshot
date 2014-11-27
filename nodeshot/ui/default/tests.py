import json
from django.core.urlresolvers import reverse
from nodeshot.core.base.tests import BaseTestCase, user_fixtures
from nodeshot.ui.default import settings


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

    def test_social_auth_optional(self):
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'social-buttons')
        # disable social auth
        setattr(settings, 'SOCIAL_AUTH_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'social-buttons')
        # re-enable social auth
        setattr(settings, 'SOCIAL_AUTH_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'social-buttons')

    def test_facebook_optional(self):
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-facebook')
        setattr(settings, 'FACEBOOK_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'btn-facebook')
        setattr(settings, 'FACEBOOK_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-facebook')

    def test_google_optional(self):
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-google')
        setattr(settings, 'GOOGLE_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'btn-google')
        setattr(settings, 'GOOGLE_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-google')

    def test_github_optional(self):
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-github')
        setattr(settings, 'GITHUB_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'btn-github')
        setattr(settings, 'GITHUB_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-github')
