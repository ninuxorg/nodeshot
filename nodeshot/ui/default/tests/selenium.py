from __future__ import absolute_import

from time import sleep
from django.core.urlresolvers import reverse
from django.test import TestCase

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node
from nodeshot.ui.default import settings as local_settings

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


class DefaultUiSeleniumTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json',
        'test_pages.json'
    ]

    INDEX_URL = '%s%s' % (local_settings.settings.SITE_URL, reverse('ui:index'))
    LEAFLET_MAP = 'Ns.body.currentView.content.currentView.map'

    def _wait_until_ajax_complete(self, seconds, message):
        """ waits until all ajax requests are complete """
        def condition(driver):
            return driver.execute_script("return typeof(jQuery) !== 'undefined' && jQuery.active === 0")
        WebDriverWait(self.browser, seconds).until(condition, message)

    def _wait_until_element_visible(self, selector, seconds, message):
        """ waits until css selector is present and visible """
        WebDriverWait(self.browser, seconds).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selector)),
            message
        )

    def _hashchange(self, hash):
        self.browser.get('%s%s' % (self.INDEX_URL, hash))
        self._wait_until_ajax_complete(10, 'Timeout')

    def _reset(self):
        """ reset and reload browser (clear localstorage and go to index) """
        self._hashchange('#/')
        self.browser.execute_script('localStorage.clear()')
        self.browser.delete_all_cookies()
        self.browser.refresh()
        self._wait_until_ajax_complete(10, 'Timeout')

    def _login(self, username='admin', password='tester', open_modal=True):
        if open_modal:
            # open sign in modal
            self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
            self._wait_until_element_visible('#js-signin-form', 3, 'signin modal not visible')
        # insert credentials
        username_field = self.browser.find_element_by_css_selector('#js-signin-form input[name=username]')
        username_field.clear()
        username_field.send_keys(username)
        password_field = self.browser.find_element_by_css_selector('#js-signin-form input[name=password]')
        password_field.clear()
        password_field.send_keys(password)
        # log in
        self.browser.find_element_by_css_selector('#js-signin-form button.btn-default').click()
        self._wait_until_ajax_complete(5, 'timeout')
        self._wait_until_element_visible('#js-username', 3, 'username after login not visible')
        # check username
        self.assertEqual(self.browser.find_element_by_css_selector('#js-username').text, 'admin')

    def _logout(self):
        # open account menu
        self.browser.find_element_by_css_selector('#js-username').click()
        # log out
        self._wait_until_element_visible('#js-logout', 3, '#js-logout not visible')
        self.browser.find_element_by_css_selector('#js-logout').click()
        self._wait_until_ajax_complete(5, 'timeout')
        # ensure UI has gone back to initial state
        self._wait_until_element_visible('#main-actions a[data-target="#signin-modal"]', 3, 'sign in link not visible after logout')

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.get(cls.INDEX_URL)
        super(DefaultUiSeleniumTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(DefaultUiSeleniumTest, cls).tearDownClass()

    def setUp(self):
        """ reset browser to initial state """
        browser = self.browser
        browser.execute_script('localStorage.clear()')
        browser.delete_all_cookies()
        browser.execute_script("Ns.db.user.clear(); Ns.db.user.trigger('logout');")
        browser.set_window_size(1100, 700)

    def test_home(self):
        self._hashchange('#')
        self.assertEqual(self.browser.find_element_by_css_selector('article.center-stage h1').text, 'Home')
        self.assertTrue(self.browser.execute_script('return Ns.db.pages.get("home") !== undefined'))
        self.assertEqual(self.browser.title, 'Home - Nodeshot')

    def test_menu_already_active(self):
        self._hashchange('#')
        # ensure clicking multiple times on a level1 menu item  still displays it as active
        self.browser.find_element_by_css_selector('#nav-bar li.active a').click()
        self.browser.find_element_by_css_selector('#nav-bar li.active a').click()
        # ensure the same on a nested menu item
        self.browser.find_element_by_css_selector('#nav-bar a.dropdown-toggle').click()
        self.browser.find_element_by_css_selector("a[href='#pages/about']").click()
        self._wait_until_ajax_complete(1, 'page timeout')
        self.browser.find_element_by_css_selector('#nav-bar li.active a.dropdown-toggle').click()
        self.browser.find_element_by_css_selector("a[href='#pages/about']").click()
        self._wait_until_ajax_complete(1, 'page timeout')
        self.browser.find_element_by_css_selector('#nav-bar li.active a.dropdown-toggle').click()

    def test_map(self):
        self._reset()
        self._hashchange('#map')
        browser = self.browser
        LEAFLET_MAP = self.LEAFLET_MAP

        # test title
        self.assertEqual(browser.title, 'Map - Nodeshot')

        # basic test
        self.assertTrue(browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'map-container'"))
        browser.find_element_by_css_selector('#map-js.leaflet-container')
        self.assertTrue(browser.execute_script("return %s._leaflet_id > -1" % LEAFLET_MAP))

        # layers control
        browser.find_element_by_css_selector('#map-js .leaflet-control-layers-list')
        LAYERS_CONTROLS = 'return _.values(%s.layerscontrol._layers)' % LEAFLET_MAP
        self.assertEqual(browser.execute_script('%s[0].name' % LAYERS_CONTROLS), 'Map')
        self.assertEqual(browser.execute_script('%s[1].name' % LAYERS_CONTROLS), 'Satellite')

        # ensure coordinates are correct
        self.assertEqual(browser.execute_script("return %s.getZoom()" % LEAFLET_MAP), local_settings.MAP_ZOOM)
        # leaflet coordinates are approximated when zoom is low, so let's check Nodeshot JS settings
        self.assertEqual(browser.execute_script("return Ns.settings.map.lat"), local_settings.MAP_CENTER[0])
        self.assertEqual(browser.execute_script("return Ns.settings.map.lng"), local_settings.MAP_CENTER[1])
        self.assertEqual(browser.execute_script("return Ns.settings.map.zoom"), local_settings.MAP_ZOOM)

        # ensure rememberCoordinates() works
        browser.execute_script("%s.setView([42.111111, 12.111111], 17)" % LEAFLET_MAP)
        sleep(0.5)
        self._hashchange('#')
        self.assertEqual(browser.execute_script("return localStorage.getObject('map').lat.toString().substr(0, 7)"), "42.1111")
        self.assertEqual(browser.execute_script("return localStorage.getObject('map').lng.toString().substr(0, 7)"), "12.1111")
        self.assertEqual(browser.execute_script("return localStorage.getObject('map').zoom"), 17)
        self._hashchange('#/map')
        self.assertEqual(browser.execute_script("return %s.getZoom()" % LEAFLET_MAP), 17)
        self.assertEqual(browser.execute_script("return %s.getCenter().lat.toString().substr(0, 7)" % LEAFLET_MAP), "42.1111")
        self.assertEqual(browser.execute_script("return %s.getCenter().lng.toString().substr(0, 7)" % LEAFLET_MAP), "12.1111")

        # map is resized when window is resized
        window_size = browser.get_window_size()

        map_size = {}
        map_size['width'] = browser.execute_script("return $('#map-js').width()")
        map_size['height'] = browser.execute_script("return $('#map-js').height()")
        browser.set_window_size(window_size['width'] - 10, window_size['height'] - 10)
        sleep(0.2)
        self.assertEqual(browser.execute_script("return $('#map-js').width()"), map_size['width'] - 10)
        self.assertEqual(browser.execute_script("return $('#map-js').height()"), map_size['height'] - 10)
        browser.set_window_size(window_size['width'], window_size['height'])
        sleep(0.2)
        self.assertEqual(browser.execute_script("return $('#map-js').width()"), map_size['width'])
        self.assertEqual(browser.execute_script("return $('#map-js').height()"), map_size['height'])

        # esnure data has been loaded
        map_objects = browser.execute_script('return Ns.body.currentView.content.currentView.collection.length')
        nodes = Node.objects.published().access_level_up_to('public').count()
        self.assertEqual(map_objects, nodes)

        # ensure clustering works
        browser.execute_script("%s.setView([42.001111, 12.611111], 7)" % LEAFLET_MAP)
        self.assertEqual(browser.execute_script('return $("#map-js .cluster.marker-active").length'), 1)
        self.assertEqual(browser.execute_script('return $("#map-js .cluster.marker-potential").length'), 1)

    def test_map_data_caching_and_reload(self):
        self._reset()
        browser = self.browser
        # ensure Ns.db.geo is empty
        self.assertTrue(browser.execute_script('return Ns.db.geo.isEmpty() === true'))
        self._hashchange('#map')
        # ensure Ns.db.geo is not empty anymore (cached)
        self.assertTrue(browser.execute_script('return Ns.db.geo.isEmpty() === false'))
        # ensure node with higher ACL not visible
        self.assertTrue(browser.execute_script("return Ns.db.geo.get('hidden-rome') === undefined"))
        # log in as admin
        self._login()
        # ensure node with higher ACL is now visible
        self.assertFalse(browser.execute_script("return Ns.db.geo.get('hidden-rome') === undefined"))
        # ensure data is not duplicated
        browser.execute_script('%s.setView([41.8879, 12.50621], 13)' % self.LEAFLET_MAP)
        browser.execute_script('$("#map-control-layer-rome").trigger("click")')
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js g')), 0)
        # log out
        self._logout()
        # ensure node with higher ACL not visible anymore
        self.assertTrue(browser.execute_script("return Ns.db.geo.get('hidden-rome') === undefined"))

    def test_map_popup(self):
        self._reset()
        self._hashchange('#/map/pomezia')
        browser = self.browser
        # changing url fragment opens popup
        self._wait_until_element_visible('#map-js .leaflet-popup-content-wrapper', 1, 'popup not visible')
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 1)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Pomezia')

        # refreshing goes back there
        browser.refresh()
        self._wait_until_element_visible('#map-js .leaflet-popup-content-wrapper', 1, 'popup not visible')
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 1)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Pomezia')

        # changing fragment goes to another element
        self._hashchange('#/map/fusolab')
        self._wait_until_element_visible('#map-js .leaflet-popup-content-wrapper', 1, 'popup not visible')
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 1)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Fusolab Rome')

        # back button supported
        browser.back()
        self._wait_until_element_visible('#map-js .leaflet-popup-content-wrapper', 1, 'popup not visible')
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Pomezia')

        # forward button supported
        browser.forward()
        self._wait_until_element_visible('#map-js .leaflet-popup-content-wrapper', 1, 'popup not visible')
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Fusolab Rome')

        # close button changes url fragment to "map"
        browser.find_element_by_css_selector('#map-js .leaflet-popup-close-button').click()
        sleep(0.3)
        self.assertEqual(browser.current_url.split('#')[1], 'map')
        # go back
        browser.back()
        self.assertIn('map/fusolab', browser.current_url.split('#')[1])
        sleep(0.2)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Fusolab Rome')
        # go forward and expect popup to be closed
        browser.forward()
        self.assertEqual(browser.current_url.split('#')[1], 'map')
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 0)

        # got to map url, no popups open
        self._hashchange('#map')
        self.assertEqual(browser.current_url.split('#')[1], 'map')
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 0)
        # simulate clicking on a popup
        browser.find_elements_by_css_selector('#map-js g')[0].click()
        # ensure popup is open
        self._wait_until_element_visible('#map-js .leaflet-popup-content-wrapper', 1, 'popup not visible')
        # url must be longer than 4 chars, eg: "map/something"
        self.assertTrue(len(browser.current_url.split('#')[1]) > 4)
        # go back
        self._hashchange('#map')

        # does not exist case
        self._hashchange('#/map/wrong')
        sleep(0.25)
        self.assertEqual(browser.find_element_by_css_selector('#tmp-modal').is_displayed(), True)
        browser.find_element_by_css_selector('#tmp-modal button').click()

    def test_map_toolbar(self):
        self._hashchange('#/map')
        browser = self.browser

        # ensure rendered
        self.assertGreater(len(browser.find_elements_by_css_selector('#map-toolbar a')), 4)
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-toolbar')), 1)

        # test base layers
        view = self.LEAFLET_MAP.replace('.map', '')
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Map._map)" % view), True)
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Satellite._map)" % view), False)
        self.assertEqual(browser.execute_script("return $('#base-layers-0').get(0).checked"), True)
        self.assertEqual(browser.execute_script("return $('#base-layers-1').get(0).checked"), False)
        # switch base layer
        browser.execute_script("$('#base-layers-1').trigger('click')")
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Map._map)" % view), False)
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Satellite._map)" % view), True)
        self.assertEqual(browser.execute_script("return $('#base-layers-0').get(0).checked"), False)
        self.assertEqual(browser.execute_script("return $('#base-layers-1').get(0).checked"), True)
        # ensure choice is mantained
        self._hashchange('#/')
        self._hashchange('#/map')
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Map._map)" % view), False)
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Satellite._map)" % view), True)
        self.assertEqual(browser.execute_script("return $('#base-layers-0').get(0).checked"), False)
        self.assertEqual(browser.execute_script("return $('#base-layers-1').get(0).checked"), True)
        # switch back to original base layer
        browser.execute_script("$('#base-layers-0').trigger('click')")
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Map._map)" % view), True)
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Satellite._map)" % view), False)
        self.assertEqual(browser.execute_script("return $('#base-layers-0').get(0).checked"), True)
        self.assertEqual(browser.execute_script("return $('#base-layers-1').get(0).checked"), False)
        # ensure choice is mantained
        self._hashchange('#/')
        self._hashchange('#/map')
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Map._map)" % view), True)
        self.assertEqual(browser.execute_script("return Boolean(%s.baseLayers.Satellite._map)" % view), False)
        self.assertEqual(browser.execute_script("return $('#base-layers-0').get(0).checked"), True)
        self.assertEqual(browser.execute_script("return $('#base-layers-1').get(0).checked"), False)

        # layers control
        browser.execute_script("%s.setView([41.87403473552959, 12.495403289794922], 10)" % self.LEAFLET_MAP)
        panel = browser.find_element_by_css_selector('#fn-map-layers')
        self.assertFalse(panel.is_displayed())
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2:not(.active)')
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2').click()
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2.active')
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-on')), 8)
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-off')), 0)
        self.assertTrue(panel.is_displayed())
        # ensure it doesn't close after clicking on it
        panel.click()
        self.assertTrue(panel.is_displayed())
        # click somewhere else to close
        self.browser.find_element_by_css_selector('#fn-map-layers-mask').click()
        self.assertFalse(panel.is_displayed())
        # ensure it reopens correctly
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2:not(.active)')
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2').click()
        sleep(0.1)
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2.active')
        self.assertTrue(panel.is_displayed())
        # expect the following leaflet layers (unfortunately numbers vary depending on screen size and system...)
        self.assertTrue(2 >= browser.execute_script("return $('#map-js path.marker-potential').length") >= 1)
        self.assertTrue(2 >= browser.execute_script("return $('#map-js path.marker-active').length") >= 1)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 1)
        # expect legend counts
        self.assertTrue(5 >= int(browser.find_element_by_css_selector('#legend-item-active .stats').text) >= 4)
        self.assertTrue(3 >= int(browser.find_element_by_css_selector('#legend-item-potential .stats').text) >= 2)

        # fix needed for headled testing
        browser.execute_script('localStorage.clear()')
        browser.refresh()

        # turn off 1 layer
        browser.execute_script('$("#map-control-layer-rome").trigger("click")')
        sleep(0.1)
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-off')), 1)
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-on')), 7)
        # ensure elements have been hidden
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 0)
        # expect legend counts
        self.assertEqual(browser.find_element_by_css_selector('#legend-item-active .stats').text, '2')
        self.assertEqual(browser.find_element_by_css_selector('#legend-item-potential .stats').text, '2')
        # turn on again
        browser.execute_script('$("#map-control-layer-rome").trigger("click")')
        # ensure elements have been shown again
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 2)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 2)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 1)
        # expect legend counts
        self.assertEqual(browser.find_element_by_css_selector('#legend-item-active .stats').text, '5')
        self.assertEqual(browser.find_element_by_css_selector('#legend-item-potential .stats').text, '3')
        # hide again
        browser.execute_script('$("#map-control-layer-rome").trigger("click")')
        # ensure choice is mantained
        self._hashchange('#/')
        self._hashchange('#/map')
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-off')), 1)
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-on')), 7)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 0)
        # test interaction with legend items - issue #171
        browser.execute_script("%s.setView([41.87403473552959, 12.495403289794922], 7)" % self.LEAFLET_MAP)
        browser.find_element_by_css_selector('#legend-item-potential a').click()
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 2)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-control-legend-potential').bootstrapSwitch('state')"), False)
        # re-enable rome layer
        browser.execute_script('$("#map-control-layer-rome").trigger("click")')
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 0)
        self.assertTrue(2 >= browser.execute_script("return $('#map-js path.marker-active').length") >= 1)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 1)
        browser.find_element_by_css_selector('#legend-item-potential a').click()
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertTrue(2 >= browser.execute_script("return $('#map-js path.marker-active').length") >= 1)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js .cluster.marker-active').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-control-legend-potential').bootstrapSwitch('state')"), True)

        # test map tools panel
        panel = browser.find_element_by_css_selector('#fn-map-tools')
        button = browser.find_element_by_css_selector('#map-toolbar .icon-tools')
        self.assertFalse(panel.is_displayed())
        button.click()
        self.assertTrue(panel.is_displayed())
        # close panel
        self.browser.find_element_by_css_selector('#fn-map-tools-mask').click()
        self.assertFalse(panel.is_displayed())

        # test toolbar hide/show on mobile
        toolbar = browser.find_element_by_css_selector('#map-toolbar')
        button = browser.find_element_by_css_selector('#toggle-toolbar')
        panel = browser.find_element_by_css_selector('#fn-map-layers')
        # open panel
        browser.find_element_by_css_selector('#map-toolbar .icon-layer-2').click()
        self.assertTrue(toolbar.is_displayed())
        self.assertFalse(button.is_displayed())
        self.assertTrue(panel.is_displayed())
        # make window narrower
        window_size = browser.get_window_size()
        browser.set_window_size(400, window_size['height'])
        # ensure toolbar hidden and button shown
        self.assertFalse(toolbar.is_displayed())
        self.assertTrue(button.is_displayed())
        self.assertFalse(panel.is_displayed())
        # show toolbar
        button.click()
        self.assertTrue(toolbar.is_displayed())
        self.assertTrue(button.is_displayed())
        # hide again
        button.click()
        self.assertFalse(toolbar.is_displayed())
        self.assertTrue(button.is_displayed())
        # reset window size to original size
        browser.set_window_size(window_size['width'], window_size['height'])
        # ensure toolbar is visible
        self.assertTrue(toolbar.is_displayed())

    def test_map_legend(self):
        self._reset()
        self._hashchange('#/map')
        browser = self.browser
        browser.execute_script("%s.setView([41.87403473552959, 12.495403289794922], 12)" % self.LEAFLET_MAP)

        # ensure legend is open
        button = browser.find_element_by_css_selector('#btn-legend.disabled')
        legend = browser.find_element_by_css_selector('#map-legend')
        self.assertTrue(legend.is_displayed())

        # ensure counts are correct
        ui_potential = int(browser.find_element_by_css_selector('#legend-item-potential .stats').text)
        ui_planned = int(browser.find_element_by_css_selector('#legend-item-planned .stats').text)
        ui_active = int(browser.find_element_by_css_selector('#legend-item-active .stats').text)
        queryset = Node.objects.published().access_level_up_to('public')
        db_potential = queryset.filter(status__slug='potential').count()
        db_planned = queryset.filter(status__slug='planned').count()
        db_active = queryset.filter(status__slug='active').count()
        self.assertEqual(ui_potential, db_potential)
        self.assertEqual(ui_planned, db_planned)
        self.assertEqual(ui_active, db_active)

        # ensure it can be closed
        browser.find_element_by_css_selector('#map-legend .icon-close').click()
        sleep(0.4)
        self.assertFalse(legend.is_displayed())
        self.assertNotIn('disabled', button.get_attribute('class'))

        # reopen again
        button.click()
        sleep(0.4)
        self.assertIn('disabled', button.get_attribute('class'))
        self.assertTrue(legend.is_displayed())

        # ensure preference is mantained when switching pages back and forth
        button.click()
        sleep(0.4)
        self.assertFalse(legend.is_displayed())
        self._hashchange('#/')
        self._hashchange('#/map')
        legend = browser.find_element_by_css_selector('#map-legend')
        self.assertFalse(legend.is_displayed())

        # reopen legend
        browser.find_element_by_css_selector('#btn-legend').click()
        # ensure groups can be hidden
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 2)
        browser.find_element_by_css_selector('#legend-item-active a').click()
        self.assertIn('disabled', browser.find_element_by_css_selector('#legend-item-active').get_attribute('class'))
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 0)
        # ensure preference is mantained
        self._hashchange('#/')
        self._hashchange('#/map')
        self.assertIn('disabled', browser.find_element_by_css_selector('#legend-item-active').get_attribute('class'))
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 0)
        # ensure it can be re-enabled
        browser.find_element_by_css_selector('#legend-item-active a').click()
        self.assertNotIn('disabled', browser.find_element_by_css_selector('#legend-item-active').get_attribute('class'))
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-potential').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js path.marker-active').length"), 2)

        # test clustering
        browser.execute_script("%s.setZoom(7)" % self.LEAFLET_MAP)
        self.assertEqual(browser.execute_script("return $('#map-js .marker-active.cluster').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js .marker-potential.cluster').length"), 1)
        browser.find_element_by_css_selector('#legend-item-active a').click()
        self.assertEqual(browser.execute_script("return $('#map-js .marker-active.cluster').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .marker-potential.cluster').length"), 1)
        browser.find_element_by_css_selector('#legend-item-active a').click()
        self.assertEqual(browser.execute_script("return $('#map-js .marker-active.cluster').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js .marker-potential.cluster').length"), 1)
        # ensure preference is mantained
        browser.find_element_by_css_selector('#legend-item-active a').click()
        self._hashchange('#/')
        self._hashchange('#/map')
        self.assertEqual(browser.execute_script("return $('#map-js .marker-active.cluster').length"), 0)
        self.assertEqual(browser.execute_script("return $('#map-js .marker-potential.cluster').length"), 1)
        # ensure it can be re-enabled
        browser.find_element_by_css_selector('#legend-item-active a').click()
        self.assertEqual(browser.execute_script("return $('#map-js .marker-active.cluster').length"), 1)
        self.assertEqual(browser.execute_script("return $('#map-js .marker-potential.cluster').length"), 1)

    def test_map_add_node(self):
        browser = self.browser
        leaflet_map = self.LEAFLET_MAP
        self._hashchange('#map')
        # test for a toggleLeafletLayers() bug
        browser.find_element_by_css_selector('#map-toolbar .icon-pin-add').click()
        self._wait_until_element_visible('#signin-modal', 1, 'signin modal not visible')
        self._hashchange('#/')
        self._wait_until_element_visible('#body article a.btn-primary', 2, 'home not visible')
        self._hashchange('#map')
        self._wait_until_element_visible('#map-js', 5, 'map not visible')
        self.assertNotEqual(browser.execute_script("return $('#map-js path').attr('fill-opacity')"), '0.3')
        browser.find_element_by_css_selector('#signin-modal .icon-close').click()
        sleep(0.5)
        # ensure "hidden" elements are visible
        legend = browser.find_element_by_css_selector('#legend-js')
        toolbar = browser.find_element_by_css_selector('#map-toolbar')
        cluster = browser.find_element_by_css_selector('#map-js .cluster')
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())
        self.assertTrue(cluster.is_displayed())
        # click on add node icon
        browser.find_element_by_css_selector('#map-toolbar .icon-pin-add').click()
        # ensure login box is shown
        self._wait_until_element_visible('#signin-modal', 1, 'signin modal not visible')

        # login as admin
        self._login(open_modal=False)
        self._wait_until_ajax_complete(5, 'timeout while reloading data after login')

        # ensure elements have been hidden
        self.assertFalse(legend.is_displayed())
        self.assertFalse(toolbar.is_displayed())
        cluster = browser.find_element_by_css_selector('#map-js .cluster')
        self.assertFalse(cluster.is_displayed())
        # ensure URL has changed
        self.assertEqual(browser.current_url.split('#')[1], 'map/add')

        # cancel step1
        self.browser.find_element_by_css_selector('#add-node-step1 button').click()
        # ensure hidden element reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())
        cluster = browser.find_element_by_css_selector('#map-js .cluster')
        self.assertTrue(cluster.is_displayed())

        self.assertEqual(browser.current_url.split('#')[1], 'map')

        # go to step2
        browser.back()
        browser.execute_script("%s.fire('click', { latlng: L.latLng(41.89727804010839, 12.504158020019531) })" % leaflet_map)
        self._wait_until_ajax_complete(5, 'timeout')

        # cancel step2
        self.browser.find_element_by_css_selector('#add-node-step2 .btn-default').click()
        # ensure hidden element reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())

        # go again to step2
        browser.find_element_by_css_selector('#map-toolbar .icon-pin-add').click()
        browser.execute_script("%s.fire('click', { latlng: L.latLng(41.89727804010839, 12.504158020019531) })" % leaflet_map)
        self._wait_until_ajax_complete(5, 'timeout')

        # confirm
        browser.find_element_by_css_selector('#add-node-step2 .btn-success').click()
        self._wait_until_element_visible('#map-add-node-js', 1, 'add node form not shown in time')
        # add node form
        browser.find_element_by_css_selector('#add-node-form-container .btn-success').click()
        self._wait_until_ajax_complete(5, 'timeout')
        # click on cancel
        browser.find_element_by_css_selector('#add-node-form-container .btn-default').click()
        sleep(0.5)  # animation
        self.assertEqual(len(browser.find_elements_by_css_selector('#add-node-form-container')), 0)

        # ensure hidden element reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())

        # go again to step2
        browser.find_element_by_css_selector('#map-toolbar .icon-pin-add').click()
        browser.execute_script("%s.fire('click', { latlng: L.latLng(41.89727804010839, 12.504158020019531) })" % leaflet_map)
        self._wait_until_ajax_complete(5, 'timeout')
        # ensure some elements are hidden
        self.assertFalse(legend.is_displayed())
        self.assertFalse(toolbar.is_displayed())
        # cancel step2
        self.browser.find_element_by_css_selector('#add-node-step2 .btn-default').click()
        # ensure hidden elements reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())

        # log out
        self._logout()

    def test_map_add_node_direct_fragment(self):
        # similar to the previous test but instead of clicking on the add node button
        # we directly open the URL fragment
        self._reset()
        browser = self.browser
        self._hashchange('#map/add')
        self._wait_until_element_visible('#signin-modal', 1, 'signin modal not visible')
        browser.find_element_by_css_selector('#signin-modal .icon-close').click()
        sleep(0.5)
        self._hashchange('#')

        # login as admin
        self._login()
        self._wait_until_ajax_complete(5, 'timeout while reloading data after login')
        self._hashchange('#map/add')

        # ensure elements have been hidden
        legend = browser.find_element_by_css_selector('#legend-js')
        toolbar = browser.find_element_by_css_selector('#map-toolbar')
        cluster = browser.find_element_by_css_selector('#map-js .cluster')
        self.assertFalse(legend.is_displayed())
        self.assertFalse(toolbar.is_displayed())
        self.assertFalse(cluster.is_displayed())
        # ensure URL has changed
        self.assertEqual(browser.current_url.split('#')[1], 'map/add')

        # cancel step1
        self.browser.find_element_by_css_selector('#add-node-step1 button').click()
        # ensure hidden element reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())
        cluster = browser.find_element_by_css_selector('#map-js .cluster')
        self.assertTrue(cluster.is_displayed())

        self.assertEqual(browser.current_url.split('#')[1], 'map')

        # log out
        self._hashchange('#')
        self._logout()

    def test_map_lat_lng(self):
        LEAFLET_MAP = self.LEAFLET_MAP
        browser = self.browser
        self._hashchange('#map/latlng/41.8625675,12.4931263')
        self.assertEqual(browser.execute_script("return %s.getCenter().lat.toString().substr(0, 8)" % LEAFLET_MAP), "41.86256")
        self.assertEqual(browser.execute_script("return %s.getCenter().lng.toString().substr(0, 8)" % LEAFLET_MAP), "12.49312")
        self.assertEqual(browser.execute_script("return %s.getZoom()" % LEAFLET_MAP), 18)
        self.assertEqual(len(browser.find_elements_by_css_selector('.leaflet-marker-icon.leaflet-zoom-animated.leaflet-clickable')), 1)

    def test_node_list(self):
        self.browser.find_element_by_css_selector('a[href="#nodes"]').click()
        self._wait_until_ajax_complete(5, 'timeout')
        self.assertTrue(self.browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'node-list'"))

        for node in Node.objects.access_level_up_to('public'):
            self.assertIn(node.name, self.browser.page_source)

    def test_node_details(self):
        # ensure not cached
        self.assertTrue(self.browser.execute_script('return Ns.db.nodes.get("pomezia") === undefined'))
        self._hashchange('#nodes/pomezia')
        self.assertTrue(self.browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'map-container'"))
        self.browser.find_element_by_css_selector('#node-details')
        self.assertIn('Pomezia', self.browser.page_source)
        # ensure cached
        self.assertFalse(self.browser.execute_script('return Ns.db.nodes.get("pomezia") === undefined'))

    def test_edit_node(self):
        # login as admin
        self._login()
        # go to edit
        self._hashchange('#nodes/pomezia/edit')
        self._wait_until_element_visible('#node-data-js form', 0.5, 'edit node form not shown in time')
        self.assertNotIn('vienna', self.browser.execute_script('return $("#node-data-js form select[name=layer]").html()'))
        # ensure leaflet popup is open
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-popup')), 1)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-marker-icon')), 1)

        # go back to node details
        self.browser.find_element_by_css_selector('#node-data-js form .btn-default').click()
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#node-data-js form')), 0)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-popup')), 0)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-marker-icon')), 0)
        self.assertIn('nodes/pomezia', self.browser.current_url)

        # go back to edit mode
        self.browser.back()
        self._wait_until_element_visible('#node-data-js form', 0.5, 'edit node form not shown in time')
        # ensure leaflet popup is open
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-popup')), 1)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-marker-icon')), 1)

        # forward to node details, temporary marker must disappear
        self.browser.forward()
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-popup')), 0)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-marker-icon')), 0)

        # go back to edit mode and click on save
        self.browser.back()
        self._wait_until_element_visible('#node-data-js form', 0.5, 'edit node form not shown in time')
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-popup')), 1)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-marker-icon')), 1)
        self.browser.find_element_by_css_selector('#node-data-js .btn-success').click()
        self._wait_until_element_visible('#node-data-js table', 0.5, 'edit node form not shown in time')
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-popup')), 0)
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#map-js .leaflet-marker-icon')), 0)

        # log out
        self._logout()

    def test_user_profile(self):
        self._hashchange('#/users/romano')
        self.assertTrue(self.browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'user-details-container'"))
        self.assertIn('romano', self.browser.page_source)

    def test_general_search(self):
        self._hashchange('#')
        search = self.browser.find_element_by_css_selector('#general-search-input')
        search.send_keys('RD')
        search.send_keys(Keys.ENTER)
        self._wait_until_ajax_complete(5, 'timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 4)
        search = self.browser.find_element_by_css_selector('#general-search-input')
        search.clear()
        search.send_keys('RDP')
        search.send_keys(Keys.ENTER)
        self._wait_until_ajax_complete(5, 'timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.browser.find_element_by_css_selector('#js-search-results li a').click()
        self._wait_until_ajax_complete(5, 'timeout')
        self.assertIn('RDP', self.browser.find_element_by_css_selector('#node-details h2').text)

    def test_general_search_address(self):
        self._hashchange('#')
        search = self.browser.find_element_by_css_selector('#general-search-input')
        search.clear()
        # no results
        search.send_keys('streetnode')
        search.send_keys(Keys.ENTER)
        self._wait_until_ajax_complete(5, 'timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.assertIn('nothing', results[0].text)
        search.send_keys(Keys.ESCAPE)
        search.clear()
        # 1 result
        search.send_keys('via Roma, Pomezia')
        search.send_keys(Keys.ENTER)
        self._wait_until_element_visible('#js-search-results li a.icon-globe', 10, 'no search address result')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.assertNotIn('nothing', results[0].text)
        search.send_keys(Keys.ESCAPE)
        search.clear()
        # 1 result
        search.send_keys('google street')
        search.send_keys(Keys.ENTER)
        self._wait_until_ajax_complete(5, 'timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.assertNotIn('nothing', results[0].text)
        search.send_keys(Keys.ESCAPE)
        search.clear()
        # 2 results
        search.send_keys('VIA delle zoccolette')
        search.send_keys(Keys.ENTER)
        self._wait_until_ajax_complete(5, 'timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 2)
        search.clear()
        # go to first result
        self.browser.find_element_by_css_selector('#js-search-results li a').click()
        self._wait_until_ajax_complete(5, 'timeout')
        self.assertIn('#map/latlng/41.89', self.browser.current_url)

    def test_notifications(self):
        self._reset()
        # login as admin
        self._login()
        self._wait_until_element_visible('#main-actions a.notifications', 1, 'notifications link not visible')
        # open notifications
        self.browser.find_element_by_css_selector('#main-actions a.notifications').click()
        self._wait_until_element_visible('#js-notifications-container .empty', 1, 'notifications panel not visible')
        self.browser.find_element_by_css_selector('#main-actions a.notifications').click()
        # log out
        self._logout()

    def test_password_reset(self):
        self._hashchange('#account/password/reset')
        self._wait_until_element_visible('#password-reset-container', 1, 'password reset container not visible')
        self._login()
        self.assertEqual(self.browser.title, 'Home - Nodeshot')

    def test_layers(self):
        self._hashchange('#layers')
        self._wait_until_element_visible('#layer-list table', 1, 'layers list not visible')
        self.assertEqual(self.browser.title, 'Layer list - Nodeshot')

    def test_layer_details(self):
        self._hashchange('#layers/rome')
        self._wait_until_element_visible('#layer-details table', 1, 'layers details not visible')
        self.assertEqual(self.browser.title, 'Rome - Nodeshot')
        self.assertTrue(self.browser.execute_script('return Ns.body.currentView.map !== undefined'))

    def test_user_nodes(self):
        self._hashchange('#users/romano/nodes')
        self._wait_until_element_visible('#node-list table', 1, 'node list not visible')
        self.assertEqual(self.browser.title, 'Nodes of user: romano - Nodeshot')
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#js-add-node')), 0)

    def test_signup_error(self):
        self._hashchange('#')
        browser = self.browser
        browser.find_element_by_css_selector('a[data-target="#signup-modal"]').click()
        sleep(0.5)
        browser.find_element_by_css_selector('#js-signup-username').send_keys('testing')
        browser.find_element_by_css_selector('#js-signup-email').send_keys('admin@admin.org')
        browser.find_element_by_css_selector('#js-signup-password').send_keys('testing')
        pwd2 = browser.find_element_by_css_selector('#js-signup-password_confirmation')
        pwd2.send_keys('testing')
        pwd2.send_keys(Keys.ENTER)
        self._wait_until_ajax_complete(10, 'Timeout')
        sleep(1)
        # ensure loading indicator is not showing anymore
        self.assertFalse(browser.find_element_by_css_selector('#loading').is_displayed())
        # ensure one error
        self.assertEqual(len(browser.find_elements_by_css_selector('.input-group.hastip.error')), 1)
        self.assertIn('address already exists', browser.find_element_by_css_selector('.tooltip-inner').text)
        browser.find_element_by_css_selector('#signup-modal .icon-close').click()

    def test_my_account(self):
        # not authenticated goes back to home
        self._hashchange('#account')
        self._wait_until_element_visible('#body article.center-stage .btn-primary', 1, 'home page not visible')
        # login
        self._login()
        self._hashchange('#account')
        self._wait_until_element_visible('#account-container', 1, 'account settings not shown after save')
        self.assertEqual(self.browser.find_element_by_css_selector('#account-container h1').text, 'My account')
        self._logout()

    def test_edit_profile(self):
        # not authenticated goes back to home
        self._hashchange('#account/profile/edit')
        self._wait_until_element_visible('#body article.center-stage .btn-primary', 1, 'home page not visible')
        # login
        self._login()
        self._hashchange('#account/profile/edit')
        self._wait_until_element_visible('#form-container', 1, 'form not shown')
        self.browser.find_element_by_css_selector('#form-container .btn-success').click()
        self._wait_until_ajax_complete(5, 'Timeout')
        self._wait_until_element_visible('#account-container', 1, 'account settings not shown after save')
        self.assertEqual(self.browser.find_element_by_css_selector('#account-container h1').text, 'My account')
        self._logout()

    def test_change_password(self):
        # not authenticated goes back to home
        self._hashchange('#account/password/change')
        self._wait_until_element_visible('#body article.center-stage .btn-primary', 1, 'home page not visible')
        # login
        self._login()
        self._hashchange('#account/password/change')
        self._wait_until_element_visible('#form-container', 1, 'form not shown')
        self.assertEqual(self.browser.find_element_by_css_selector('#body article h1').text, 'Change account password')
        self.browser.find_element_by_css_selector('#form-container .btn-success').click()
        self._wait_until_ajax_complete(5, 'Timeout')
        self.assertEqual(len(self.browser.find_elements_by_css_selector('#form-container .has-error')), 2)
        self._logout()
