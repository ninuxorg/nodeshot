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
    LEAFLET_MAP = 'Ns.body.currentView.content.currentView.map'

    def _hashchange(self, hash):
        self.browser.get('%s%s' % (self.INDEX_URL, hash))
        WebDriverWait(self.browser, 10).until(ajax_complete, 'Timeout')

    def _reset(self):
        """ reset and reload browser (clear localstorage and go to index) """
        self._hashchange('#/')
        self.browser.execute_script('localStorage.clear()')
        self.browser.delete_all_cookies()
        self.browser.refresh()

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.get(cls.INDEX_URL)
        super(DefaultUiTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(DefaultUiTest, cls).tearDownClass()

    def setUp(self):
        """ reset browser to initial state """
        browser = self.browser
        browser.execute_script('localStorage.clear()')
        browser.delete_all_cookies()
        browser.execute_script("Ns.db.user.clear(); Ns.db.user.trigger('logout');")
        browser.set_window_size(1100, 700)

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
        self._reset()
        self._hashchange('#map')
        browser = self.browser
        LEAFLET_MAP = self.LEAFLET_MAP
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
        self.assertEqual(browser.execute_script("return localStorage.getObject('map').lat.toString().substr(0, 8)"), "42.11111")
        self.assertEqual(browser.execute_script("return localStorage.getObject('map').lng.toString().substr(0, 8)"), "12.11111")
        self.assertEqual(browser.execute_script("return localStorage.getObject('map').zoom"), 17)
        self._hashchange('#/map')
        self.assertEqual(browser.execute_script("return %s.getZoom()" % LEAFLET_MAP), 17)
        self.assertEqual(browser.execute_script("return %s.getCenter().lat.toString().substr(0, 8)" % LEAFLET_MAP), "42.11111")
        self.assertEqual(browser.execute_script("return %s.getCenter().lng.toString().substr(0, 8)" % LEAFLET_MAP), "12.11111")

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
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.2)
        username = self.browser.find_element_by_css_selector('#js-signin-form input[name=username]')
        username.clear()
        username.send_keys('admin')
        password = self.browser.find_element_by_css_selector('#js-signin-form input[name=password]')
        password.clear()
        password.send_keys('tester')
        self.browser.find_element_by_css_selector('#js-signin-form button.btn-default').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Login timeout')
        sleep(0.3)
        # ensure node with higher ACL is now visible
        self.assertFalse(browser.execute_script("return Ns.db.geo.get('hidden-rome') === undefined"))

        # log out
        self.browser.find_element_by_css_selector('#js-username').click()
        self.browser.find_element_by_css_selector('#js-logout').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Logout timeout')

        # ensure node with higher ACL not visible anymore
        self.assertTrue(browser.execute_script("return Ns.db.geo.get('hidden-rome') === undefined"))

    def test_map_popup(self):
        self._reset()
        self._hashchange('#/map/pomezia')
        browser = self.browser
        # changing url fragment opens popup
        sleep(0.2)
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 1)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Pomezia')

        # refreshing goes back there
        browser.refresh()
        sleep(0.2)
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 1)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Pomezia')

        # changing fragment goes to another element
        self._hashchange('#/map/fusolab')
        sleep(0.2)
        self.assertEqual(len(browser.find_elements_by_css_selector('#map-js .leaflet-popup-content-wrapper')), 1)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Fusolab Rome')

        # back button supported
        browser.back()
        sleep(0.3)
        self.assertEqual(browser.find_element_by_css_selector('#map-js .leaflet-popup-content-wrapper h4').text, 'Pomezia')

        # forward button supported
        browser.forward()
        sleep(0.3)
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
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-on')), 7)
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
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-on')), 6)
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
        self.assertEqual(len(browser.find_elements_by_css_selector('#fn-map-layers .switch-on')), 6)
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

        # open search address panel
        panel = browser.find_element_by_css_selector('#fn-search-address')
        button = browser.find_element_by_css_selector('#map-toolbar .icon-search')
        self.assertFalse(panel.is_displayed())
        button.click()
        self.assertTrue(panel.is_displayed())
        # perform search
        input = browser.find_element_by_css_selector('#fn-search-address input')
        submit = browser.find_element_by_css_selector('#fn-search-address button')
        input.send_keys('Via Silvio Pellico, Pomezia, Italy')
        submit.click()
        WebDriverWait(browser, 5).until(ajax_complete, 'Search address timeout')
        self.assertEqual(browser.execute_script('return typeof(Ns.body.currentView.panels.currentView.addressMarker)'), 'object')
        self.assertEqual(browser.execute_script('return Ns.body.currentView.content.currentView.map.getZoom()'), 18)
        input.clear()
        # close panel
        self.browser.find_element_by_css_selector('#fn-search-address-mask').click()
        self.assertFalse(panel.is_displayed())
        self.assertEqual(browser.execute_script('return typeof(Ns.body.currentView.panels.currentView.addressMarker)'), 'object')
        sleep(4.55)
        self.assertEqual(browser.execute_script('return typeof(Ns.body.currentView.panels.currentView.addressMarker)'), 'undefined')

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
        sleep(0.3)
        self.assertFalse(legend.is_displayed())
        self.assertNotIn('disabled', button.get_attribute('class'))

        # reopen again
        button.click()
        sleep(0.3)
        self.assertIn('disabled', button.get_attribute('class'))
        self.assertTrue(legend.is_displayed())

        # ensure preference is mantained when switching pages back and forth
        button.click()
        sleep(0.3)
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
        sleep(0.2)
        self._hashchange('#/')
        sleep(0.1)
        self._hashchange('#map')
        sleep(0.1)
        self.assertNotEqual(browser.execute_script("return $('#map-js path').attr('fill-opacity')"), '0.3')
        browser.find_element_by_css_selector('#signin-modal .icon-close').click()

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
        sleep(0.5)
        self.assertTrue(browser.find_element_by_css_selector('#signin-modal').is_displayed())

        # login
        username = self.browser.find_element_by_css_selector('#js-signin-form input[name=username]')
        username.clear()
        username.send_keys('admin')
        password = self.browser.find_element_by_css_selector('#js-signin-form input[name=password]')
        password.clear()
        password.send_keys('tester')
        self.browser.find_element_by_css_selector('#js-signin-form button.btn-default').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Login timeout')

        # ensure elements have been hidden
        sleep(0.3)
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
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search address timeout')

        # cancel step2
        self.browser.find_element_by_css_selector('#add-node-step2 .btn-default').click()
        # ensure hidden element reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())

        # go again to step2
        browser.find_element_by_css_selector('#map-toolbar .icon-pin-add').click()
        browser.execute_script("%s.fire('click', { latlng: L.latLng(41.89727804010839, 12.504158020019531) })" % leaflet_map)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search address timeout')

        # confirm
        browser.find_element_by_css_selector('#add-node-step2 .btn-success').click()
        sleep(0.8)  # animation
        # add node form
        self.assertTrue(browser.find_element_by_css_selector('#map-add-node-js').is_displayed())
        browser.find_element_by_css_selector('#add-node-form .btn-success').click()
        WebDriverWait(browser, 5).until(ajax_complete, 'Submit timeout')
        self.assertNotEqual(browser.find_element_by_css_selector('#add-node-form .error-msg').text, '')
        # click on cancel
        browser.find_element_by_css_selector('#add-node-form .btn-default').click()
        sleep(0.5)  # animation
        self.assertEqual(len(browser.find_elements_by_css_selector('#add-node-form')), 0)

        # ensure hidden element reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())

        # go again to step2
        browser.find_element_by_css_selector('#map-toolbar .icon-pin-add').click()
        browser.execute_script("%s.fire('click', { latlng: L.latLng(41.89727804010839, 12.504158020019531) })" % leaflet_map)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search address timeout')
        # ensure some elements are hidden
        self.assertFalse(legend.is_displayed())
        self.assertFalse(toolbar.is_displayed())
        # cancel step2
        self.browser.find_element_by_css_selector('#add-node-step2 .btn-default').click()
        # ensure hidden elements reset to initial state
        self.assertTrue(legend.is_displayed())
        self.assertTrue(toolbar.is_displayed())

        # log out
        self.browser.find_element_by_css_selector('#js-username').click()
        self.browser.find_element_by_css_selector('#js-logout').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Logout timeout')
        # ensure UI has gone back to initial state
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]')

    def test_map_lat_lng(self):
        LEAFLET_MAP = self.LEAFLET_MAP
        browser = self.browser
        self._hashchange('#map/latlng/41.8625675,12.4931263')
        self.assertEqual(browser.execute_script("return %s.getCenter().lat.toString().substr(0, 8)" % LEAFLET_MAP), "41.86256")
        self.assertEqual(browser.execute_script("return %s.getCenter().lng.toString().substr(0, 8)" % LEAFLET_MAP), "12.49312")
        self.assertEqual(browser.execute_script("return %s.getZoom()" % LEAFLET_MAP), 18)
        self.assertEqual(len(browser.find_elements_by_css_selector('.leaflet-marker-icon.leaflet-zoom-animated.leaflet-clickable')), 1)

    def test_node_list(self):
        self.browser.find_element_by_css_selector('a[href="#/nodes"]').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Node list timeout')
        self.assertTrue(self.browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'node-list'"))

        for node in Node.objects.access_level_up_to('public'):
            self.assertIn(node.name, self.browser.page_source)

    def test_node_details(self):
        self._hashchange('#/nodes/pomezia')
        self.assertTrue(self.browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'map-container'"))
        self.browser.find_element_by_css_selector('#node-details')
        self.assertIn('Pomezia', self.browser.page_source)

    def test_user_profile(self):
        self._hashchange('#/users/romano')
        self.assertTrue(self.browser.execute_script("return Ns.body.currentView.$el.attr('id') == 'user-details-container'"))
        self.assertIn('romano', self.browser.page_source)

    def test_login_and_logout(self):
        # open sign in modal
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.2)
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

    def test_general_search_address(self):
        self._hashchange('#')
        search = self.browser.find_element_by_css_selector('#general-search-input')
        search.clear()
        # no results
        search.send_keys('streetnode')
        search.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.assertIn('nothing', results[0].text)
        search.send_keys(Keys.ESCAPE)
        search.clear()
        # 1 result
        search.send_keys('via Roma, Pomezia')
        search.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.assertNotIn('nothing', results[0].text)
        search.send_keys(Keys.ESCAPE)
        search.clear()
        # 1 result
        search.send_keys('google street')
        search.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Search timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 1)
        self.assertNotIn('nothing', results[0].text)
        search.send_keys(Keys.ESCAPE)
        search.clear()
        # 2 results
        search.send_keys('VIA delle zoccolette')
        search.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Go to search result timeout')
        results = self.browser.find_elements_by_css_selector('#js-search-results li')
        self.assertEqual(len(results), 2)
        search.clear()
        # go to first result
        self.browser.find_element_by_css_selector('#js-search-results li a').click()
        WebDriverWait(self.browser, 5).until(ajax_complete, 'Go to search result timeout')
        self.assertIn('#/map/latlng/41.89', self.browser.current_url)

    def test_notifications(self):
        # open sign in modal
        self.browser.find_element_by_css_selector('#main-actions a[data-target="#signin-modal"]').click()
        sleep(0.2)
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
        sleep(0.2)

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
