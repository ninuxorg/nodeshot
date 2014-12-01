import json
from time import sleep

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.conf import settings

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node
from nodeshot.ui.default import settings as local_settings

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException


def ajax_complete(driver):
    try:
        return driver.execute_script("return jQuery.active == 0")
    except WebDriverException:
        pass


class DefaultUiTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]

    INDEX_URL = '%s%s' % (settings.SITE_URL, reverse('ui:index'))

    def _hashchange(self, hash):
        self.browser.get('%s%s' % (self.INDEX_URL, hash))
        WebDriverWait(self.browser, 10).until(ajax_complete, 'Timeout')

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.get(cls.INDEX_URL)
        cls.browser.css = cls.browser.find_element_by_css_selector
        super(DefaultUiTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(DefaultUiTest, cls).tearDownClass()

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

    def test_home(self):
        self._hashchange('#')
        self.assertEqual(self.browser.css('article.center-stage h1').text, 'Home')

    def test_menu_already_active(self):
        self._hashchange('#')
        # ensure clicking multiple times on a level1 menu item  still displays it as active
        self.browser.css('#nav-bar li.active a').click()
        self.browser.css('#nav-bar li.active a').click()
        # ensure the same on a nested menu item
        self.browser.css('#nav-bar a.dropdown-toggle').click()
        self.browser.css("a[href='#/pages/about']").click()
        self.browser.css('#nav-bar li.active a.dropdown-toggle').click()
        self.browser.css("a[href='#/pages/about']").click()
        self.browser.css('#nav-bar li.active a.dropdown-toggle').click()

    def test_map(self):
        self._hashchange('#/map')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'map-container'"))

    def test_node_list(self):
        self.browser.css('a[href="#/nodes"]').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Timeout')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'node-list'"))

        for node in Node.objects.access_level_up_to('public'):
            self.assertIn(node.name, self.browser.page_source)

    def test_node_details(self):
        self._hashchange('#/nodes/pomezia')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'map-container'"))
        self.browser.css('#node-details')
        self.assertIn('Pomezia', self.browser.page_source)

    def test_user_profile(self):
        self._hashchange('#/users/romano')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'user-details-container'"))
        self.assertIn('romano', self.browser.page_source)

    def test_authentication(self):
        # open sign in modal
        self.browser.css('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.5)
        # insert credentials
        username = self.browser.css('#js-signin-form input[name=username]')
        username.send_keys('admin')
        password = self.browser.css('#js-signin-form input[name=password]')
        password.send_keys('tester')
        # log in
        self.browser.css('#js-signin-form button.btn-default').click()
        # check username
        self.assertEqual(self.browser.css('#js-username').text, 'admin')
        # open account menu
        self.browser.css('#js-username').click()
        # log out
        self.browser.css('#js-logout').click()
        sleep(0.3)
        # ensure UI has gone back to initial state
        self.browser.css('#main-actions a[data-target="#signin-modal"]')
