from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from nodeshot.core.base.tests import user_fixtures
from nodeshot.networking.net.models import Interface

from ..models import Link, Topology
from ..models.choices import LINK_STATUS, LINK_TYPES
from ..exceptions import LinkDataNotFound, LinkNotFound


class LinkTest(TestCase):
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
        super(LinkTest, self).setUp()
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

    def test_auto_link_type(self):
        link = self.link
        link.type = None
        link.save()
        link = Link.objects.find(link.id)
        self.assertEqual(link.type, LINK_TYPES.get('radio'))

    def test_get_link(self):
        self.assertEqual(Link.get_link(source='172.16.41.42', target='172.16.40.22').pk, 1)
        self.assertEqual(Link.get_link(source='172.16.40.22', target='172.16.41.42').pk, 1)
        self.assertEqual(Link.get_link(source='00:27:22:00:50:71', target='00:27:22:00:50:72').pk, 1)
        self.assertEqual(Link.get_link(source='00:27:22:00:50:72', target='00:27:22:00:50:71').pk, 1)

    def test_get_link_topology_none(self):
        l = Link.get_link(source='172.16.41.42', target='172.16.40.22')
        l.topology = Topology.objects.first()
        l.save()
        self.assertEqual(Link.get_link(source='172.16.41.42', target='172.16.40.22').pk, 1)

    def test_link_not_found(self):
        with self.assertRaises(LinkNotFound):
            Link.get_link(source='00:27:22:00:50:72', target='00:27:22:38:13:E4')

    def test_link_data_not_found(self):
        # one interface not found
        try:
            Link.get_link(source='00:27:22:00:50:72', target='CC:27:22:00:BB:AA')
        except LinkDataNotFound as e:
            self.assertIn('CC:27:22:00:BB:AA', str(e))
        else:
            self.fail('LinkDataNotFound not raised')
        # both interfaces not found
        try:
            Link.get_link(source='00:27:22:DD:BB:CC', target='CC:27:22:00:BB:AA')
        except LinkDataNotFound as e:
            self.assertIn('00:27:22:DD:BB:CC', str(e))
            self.assertIn('CC:27:22:00:BB:AA', str(e))
        else:
            self.fail('LinkDataNotFound not raised')

    def test_get_link_value_error(self):
        with self.assertRaises(ValueError):
            Link.get_link(source='127.0.0.1', target='00:27:22:00:50:71')

    def test_link_get_or_create(self):
        # preparation
        Link.objects.delete()
        self.assertEqual(Link.objects.count(), 0)
        # create link
        link = Link.get_or_create(source='172.16.41.42', target='172.16.40.22', cost=1.1)
        self.assertIsInstance(link, Link)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.metric_value, 1.1)
        # second time does not create
        link2 = Link.get_or_create(source='172.16.41.42', target='172.16.40.22', cost=1.1)
        # ensure same object
        self.assertEqual(link.pk, link2.pk)
        self.assertEqual(Link.objects.count(), 1)

    def test_link_test_link_get_or_create_with_topology(self):
        # preparation
        Link.objects.delete()
        self.assertEqual(Link.objects.count(), 0)
        t = Topology.objects.first()
        # create link
        link = Link.get_or_create(source='172.16.41.42',
                                  target='172.16.40.22',
                                  cost=1.1,
                                  topology=t)
        self.assertIsInstance(link, Link)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(link.status, LINK_STATUS['active'])
        self.assertEqual(link.metric_value, 1.1)
        self.assertEqual(link.topology.id, t.id)
        # second time does not create
        link2 = Link.get_or_create(source='172.16.41.42',
                                   target='172.16.40.22',
                                   cost=1.1,
                                   topology=t)
        # ensure same object
        self.assertEqual(link.pk, link2.pk)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(link.topology.id, t.id)

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
