"""
nodeshot.core.cms unit tests
"""

import simplejson as json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from nodeshot.core.base.tests import user_fixtures

from .models import *


class CMSTest(TestCase):

    fixtures = [
        'initial_data.json',
        user_fixtures,
    ]

    def setUp(self):
        pass

    def test_page_list(self):
        url = reverse('api_page_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Page.objects.count())

    def test_page_detail(self):
        url = reverse('api_page_detail', args=['privacy-policy'])
        response = self.client.get(url)
        self.assertContains(response, 'privacy-policy')

    def test_menu_list(self):
        url = reverse('api_menu_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
