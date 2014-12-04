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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


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
        self.assertEqual(self.browser.find_element_by_css_selector('article.center-stage h1').text, 'Home')

    def test_menu_already_active(self):
        self._hashchange('#')
        # ensure clicking multiple times on a level1 menu item  still displays it as active
        self.browser.find_element_by_css_selector('#nav-bar li.active a').click()
        self.browser.find_element_by_css_selector('#nav-bar li.active a').click()
        # ensure the same on a nested menu item
        self.browser.find_element_by_css_selector('#nav-bar a.dropdown-toggle').click()
        self.browser.find_element_by_css_selector("a[href='#/pages/about']").click()
        self.browser.find_element_by_css_selector('#nav-bar li.active a.dropdown-toggle').click()
        self.browser.find_element_by_css_selector("a[href='#/pages/about']").click()
        self.browser.find_element_by_css_selector('#nav-bar li.active a.dropdown-toggle').click()

    def test_map(self):
        self._hashchange('#/map')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'map-container'"))
        self.browser.find_element_by_css_selector('#map-js.leaflet-container')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.map._leaflet_id > -1"))

    def test_map_legend(self):
        self._hashchange('#/map')
        button = self.browser.find_element_by_css_selector('#btn-legend.disabled')
        legend = self.browser.find_element_by_css_selector('#map-legend')
        self.browser.find_element_by_css_selector('#map-legend .icon-close').click()
        sleep(0.5)
        self.assertFalse(legend.is_displayed())
        self.assertNotIn('disabled', button.get_attribute('class'))
        button.click()
        sleep(0.5)
        self.assertIn('disabled', button.get_attribute('class'))
        self.assertTrue(legend.is_displayed())

    def test_node_list(self):
        self.browser.find_element_by_css_selector('a[href="#/nodes"]').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Node list timeout')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'node-list'"))

        for node in Node.objects.access_level_up_to('public'):
            self.assertIn(node.name, self.browser.page_source)

    def test_node_details(self):
        self._hashchange('#/nodes/pomezia')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'map-container'"))
        self.browser.find_element_by_css_selector('#node-details')
        self.assertIn('Pomezia', self.browser.page_source)

    def test_user_profile(self):
        self._hashchange('#/users/romano')
        self.assertTrue(self.browser.execute_script("return Nodeshot.body.currentView.$el.attr('id') == 'user-details-container'"))
        self.assertIn('romano', self.browser.page_source)

    def test_login_and_logout(self):
        # open sign in modal
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.5)
        # insert credentials
        username = self.browser.find_element_by_css_selector('#js-signin-form input[name=username]')
        username.clear()
        username.send_keys('admin')
        password = self.browser.find_element_by_css_selector('#js-signin-form input[name=password]')
        password.clear()
        password.send_keys('tester')
        # log in
        self.browser.find_element_by_css_selector('#js-signin-form button.btn-default').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Login timeout')
        # check username
        self.assertEqual(self.browser.find_element_by_css_selector('#js-username').text, 'admin')
        # open account menu
        self.browser.find_element_by_css_selector('#js-username').click()
        # log out
        self.browser.find_element_by_css_selector('#js-logout').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Logout timeout')
        # ensure UI has gone back to initial state
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]')

    def test_general_search(self):
        self._hashchange('#')
        search = self.browser.find_element_by_css_selector('#general-search-input')
        search.send_keys('RD')
        search.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 4)
        search = self.browser.find_element_by_css_selector('#general-search-input')
        search.clear()
        search.send_keys('RDP')
        search.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Go to search result timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.browser.find_element_by_css_selector('#js-search-results li a').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Go to search result timeout')
        self.assertIn('RDP', self.browser.find_element_by_css_selector('#node-details h2').text)

    def test_notifications(self):
        # open sign in modal
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.5)
        # insert credentials
        username = self.browser.find_element_by_css_selector('#js-signin-form input[name=username]')
        username.clear()
        username.send_keys('admin')
        password = self.browser.find_element_by_css_selector('#js-signin-form input[name=password]')
        password.clear()
        password.send_keys('tester')
        # log in
        self.browser.find_element_by_css_selector('#js-signin-form button.btn-default').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Login timeout')

        # open notifications
        self.browser.find_element_by_css_selector('#main-actions a.notifications').click()
        self.browser.find_element_by_css_selector('#js-notifications-container .empty')
        self.browser.find_element_by_css_selector('#main-actions a.notifications').click()

        # open account menu
        self.browser.find_element_by_css_selector('#js-username').click()
        # log out
        self.browser.find_element_by_css_selector('#js-logout').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Logout timeout')
        # ensure UI has gone back to initial state
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]')

    def test_add_node(self):
        # open sign in modal
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.5)  # animation
        # insert credentials
        username = self.browser.find_element_by_css_selector('#js-signin-form input[name=username]')
        username.clear()
        username.send_keys('admin')
        password = self.browser.find_element_by_css_selector('#js-signin-form input[name=password]')
        password.clear()
        password.send_keys('tester')
        # log in
        self.browser.find_element_by_css_selector('#js-signin-form button.btn-default').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Login timeout')

        # click on add node button
        self._hashchange('#/map')
        sleep(0.5)  # animation
        a = self.browser.find_element_by_css_selector('#map-toolbar a.icon-pin-add')
        a.click()
        self.browser.find_element_by_css_selector('#add-node-step1 .btn-default').click()
        a.click()
        self.browser.execute_script('Nodeshot.body.currentView.map.setView([41.86741963140808, 12.507655620574951], 18)')
        self.browser.find_element_by_css_selector('#add-node-step1')
        map_element = self.browser.find_element_by_css_selector('#map-js')
        actions = ActionChains(self.browser)
        actions.move_to_element_with_offset(map_element, 50, 50)
        map_element.click()
        # confirm
        self.browser.find_element_by_css_selector('#add-node-step2 .btn-success').click()
        sleep(0.5)  # animation
        # add node form
        self.assertTrue(self.browser.find_element_by_css_selector('#add-node-container').is_displayed())
        self.browser.find_element_by_css_selector('#add-node-container .btn-success').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Login timeout')
        self.assertNotEqual(self.browser.find_element_by_css_selector('#add-node-container .error-msg').text, '')
        self.browser.find_element_by_css_selector('#add-node-container .btn-default').click()
        sleep(0.5)  # animation
        self.assertFalse(self.browser.find_element_by_css_selector('#add-node-container').is_displayed())

        # open account menu
        self.browser.find_element_by_css_selector('#js-username').click()
        # log out
        self.browser.find_element_by_css_selector('#js-logout').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Logout timeout')
        # ensure UI has gone back to initial state
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]')
