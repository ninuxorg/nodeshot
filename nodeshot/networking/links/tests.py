"""
nodeshot.networking.links unit tests
"""

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures
from nodeshot.networking.net.models import Interface

from .models import Link
from .models.choices import LINK_STATUS, LINK_TYPES


class LinkTest(BaseTestCase):

    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_routing_protocols.json',
        'test_devices.json',
        'test_interfaces.json',
        'test_ip_addresses.json',
        'test_links'
    ]

    def setUp(self):
        l = Link()
        l.interface_a = Interface.objects.find(2)
        l.interface_b = Interface.objects.find(3)
        l.type = LINK_TYPES.get('radio')
        l.status = LINK_STATUS.get('active')
        self.link = l

    def test_non_radio_shouldnt_have_radio_info(self):
        """ *** A link of any type which is not "radio" should not have dBm or noise data *** """
        link = self.link
        link.type = LINK_TYPES.get('ethernet')
        link.dbm = -70
        link.noise = -90
        self.assertRaises(ValidationError, link.full_clean)

    def test_save_radio_link(self):
        """ *** It should be possible to save a new link *** """
        l = self.link
        l.type = LINK_TYPES.get('radio')
        l.dbm = -70
        l.noise = -90
        l.save()
        # delete variable l
        del l
        # retrieve link again from DB
        l = Link.objects.last()
        # check everything worked
        self.assertTrue(l.type == 1 and l.dbm == -70 and l.noise == -90, "something went wrong while saving a new link")

    def test_null_interfaces(self):
        """ *** An active link with null 'from interface' and 'to interface' fields should not be saved  *** """
        l = Link(type=LINK_TYPES.get('radio'), status=LINK_TYPES.get('active'))
        self.assertRaises(ValidationError, l.full_clean)

    def test_auto_fill_node_fields(self):
        """ *** When a link with any type except for 'planned' is saved it should automatically fill the fields 'from node' and 'to node'  *** """
        l = self.link
        l.type = LINK_TYPES.get('radio')
        l.save()
        self.assertTrue(l.node_a is not None and l.node_b is not None, '"from node" and "to node" fields are null')

    def test_null_interface_and_node_fields(self):
        """ *** It should not be possible to save a link which has void node and interface info  *** """
        link = Link(type=LINK_TYPES.get('radio'), status=LINK_STATUS.get('planned'))
        self.assertRaises(ValidationError, link.full_clean)

    def test_same_to_and_from_interface(self):
        link = self.link
        link.interface_a = Interface.objects.find(1)
        link.interface_b = Interface.objects.find(1)
        with self.assertRaises(ValidationError):
            link.full_clean()

        link2 = self.link
        link2.interface_b_id = 1
        link2.interface_a_id = 1
        with self.assertRaises(ValidationError):
            link.full_clean()

    def test_auto_linestring(self):
        link = self.link
        self.assertIsNone(link.line)
        link.save()
        self.assertIsNotNone(link.line)

    def test_additional_properties(self):
        link = self.link
        link.interface_b = Interface.objects.find(3)  # different node
        self.assertIsNone(link.node_a_name)
        self.assertIsNone(link.node_b_name)
        self.assertIsNone(link.node_a_slug)
        self.assertIsNone(link.node_b_slug)
        self.assertIsNone(link.interface_a_mac)
        self.assertIsNone(link.interface_b_mac)
        link.save()
        link = Link.objects.find(link.id)
        self.assertEqual(link.node_a_name, link.node_a.name)
        self.assertEqual(link.node_b_name, link.node_b.name)
        self.assertEqual(link.node_a_slug, link.node_a.slug)
        self.assertEqual(link.node_b_slug, link.node_b.slug)
        self.assertEqual(link.interface_a_mac, link.interface_a.mac)
        self.assertEqual(link.interface_b_mac, link.interface_b.mac)

    def test_link_interface_type(self):
        link = self.link
        link.interface_a = Interface.objects.find(1)  # ethernet, while interface_b is wireless

        with self.assertRaises(ValidationError):
            link.full_clean()

    def test_auto_link_type(self):
        link = self.link
        link.type = None
        link.save()
        link = Link.objects.find(link.id)
        self.assertEqual(link.type, LINK_TYPES.get('radio'))

    def test_links_api(self):
        link = self.link
        link.save()
        link = Link.objects.find(link.id)

        # GET: 200 - link list
        url = reverse('api_link_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

        # GET: 200 - link list geojson
        url = reverse('api_links_geojson_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(len(response.data['features']), 2)

        # GET: 200 - link details
        url = reverse('api_link_details', args=[link.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        # GET: 200 - link details geojson
        url = reverse('api_links_geojson_details', args=[link.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_node_links_api(self):
        link = self.link
        link.save()
        link = Link.objects.find(link.id)

        # GET: 200 - node A
        url = reverse('api_node_links', args=[link.node_a.slug])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 2)

        # GET: 200 - node B
        url = reverse('api_node_links', args=[link.node_b.slug])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 2)

        # GET: 404
        url = reverse('api_node_links', args=['idontexist'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
