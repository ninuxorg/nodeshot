from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase

from nodeshot.core.base.tests import user_fixtures
from nodeshot.ui.default import settings as local_settings


class DefaultUiDjangoTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json',
    ]

    def test_index(self):
        response = self.client.get(reverse('ui:index'))
        self.assertEqual(response.status_code, 200)

    def test_social_auth_optional(self):
        # enable social auth
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'social-buttons')
        # disable social auth
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'social-buttons')

    def test_facebook_optional(self):
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', True)
        setattr(local_settings, 'FACEBOOK_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-facebook')
        setattr(local_settings, 'FACEBOOK_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'btn-facebook')
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', False)

    def test_google_optional(self):
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', True)
        setattr(local_settings, 'GOOGLE_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-google')
        setattr(local_settings, 'GOOGLE_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'btn-google')
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', False)

    def test_github_optional(self):
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', True)
        setattr(local_settings, 'GITHUB_ENABLED', True)
        response = self.client.get(reverse('ui:index'))
        self.assertContains(response, 'btn-github')
        setattr(local_settings, 'GITHUB_ENABLED', False)
        response = self.client.get(reverse('ui:index'))
        self.assertNotContains(response, 'btn-github')
        setattr(local_settings, 'SOCIAL_AUTH_ENABLED', False)
