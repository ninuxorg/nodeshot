from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.base.choices import ACCESS_LEVELS

from .models import *


class CMSTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
    ]

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

    def test_menu_list_check_nested(self):
        url = reverse('api_menu_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # ensure there are the correct amount of children in the JSON response
        got_children = MenuItem.objects.get(name='About')
        self.assertEqual(len(response.data[got_children.id-1]['children']), got_children.menuitem_set.count())
    
    def test_menu_list_check_acl(self):
        url = reverse('api_menu_list')
        # ensure link is public
        response = self.client.get(url)
        self.assertIn('Software Credits', response.content)
        # set about menu item as restricted access
        item = MenuItem.objects.get(name='Software Credits')
        item.access_level = ACCESS_LEVELS.get('trusted')
        item.save()
        # ensure menu item is public anymore
        response = self.client.get(url)
        self.assertNotIn('Software Credits', response.content)
        # ensure admin can see it
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        self.assertIn('Software Credits', response.content)

    def test_nested_menu_item(self):
        new = MenuItem()
        new.name = 'new'
        new.url = '#'
        new.full_clean()  # validation should be ok

        # set a parent which already has a parent
        new.parent = MenuItem.objects.exclude(parent=None).first()
        with self.assertRaises(ValidationError):
            new.full_clean()
