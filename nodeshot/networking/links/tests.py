"""
nodeshot.core.links unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from nodeshot.networking.net.models import Interface

from .models import Link
from .choices import LINK_STATUS, LINK_TYPE


class LinkTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
        'test_layers.json',
        'test_nodes.json',
        'test_routing_protocols.json',
        'test_devices.json',
        'test_interfaces.json',
        'test_ip_addresses.json'
    ]
    
    def setUp(self):
        l = Link()
        l.interface_a = Interface.objects.get(pk=1)
        l.interface_b = Interface.objects.get(pk=2)
        l.type = LINK_TYPE.get('fiber')
        l.status = LINK_STATUS.get('active')
        l.dbm = -70
        l.noise = -90
        self.link = l
    
    def test_non_radio_shouldnt_have_radio_info(self):
        """ *** A link of any type which is not "radio" should not have dBm or noise data *** """
        self.assertRaises(ValidationError, self.link.full_clean)
    
    def test_save_radio_link(self):
        """ *** It should be possible to save a new link *** """
        l = self.link
        l.type = LINK_TYPE.get('radio')
        l.save()
        # delete variable l
        del l
        # retrieve link again from DB
        l = Link.objects.all()[0]
        # check everything worked
        self.assertTrue(l.type == 1 and l.dbm == -70 and l.noise == -90, "something went wrong while saving a new link")
    
    def test_null_interfaces(self):
        """ *** An active link with null 'from interface' and 'to interface' fields should not be saved  *** """
        l = Link(type=LINK_TYPE.get('radio'), status=LINK_TYPE.get('active'))
        self.assertRaises(ValidationError, l.full_clean)
    
    def test_auto_fill_node_fields(self):
        """ *** When a link with any type except for 'planned' is saved it should automatically fill the fields 'from node' and 'to node'  *** """
        l = self.link
        l.type = LINK_TYPE.get('radio')
        l.save()
        self.assertTrue(l.node_a != None and l.node_b != None, '"from node" and "to node" fields are null')
    
    def test_null_interface_and_node_fields(self):
        """ *** It should not be possible to save a link which has void node and interface info  *** """
        link = Link(type=LINK_TYPE.get('radio'), status=LINK_STATUS.get('planned'))
        self.assertRaises(ValidationError, link.full_clean)
    
    def test_link_manager(self):
        """ test link manager """
        self.link.save()
        self.assertEqual(Link.objects.layer('rome').count(), 1, "LinkManager layer slug lookup failed for layer 'rome'")
        self.assertEqual(Link.objects.layer(1).count(), 1, "LinkManager layer id lookup failed for layer 'rome'")
        self.assertEqual(Link.objects.layer('rome')[0].dbm, -70, "LinkManager dbm assert equal failed")
        self.assertEqual(Link.objects.layer('pisa').count(), 0, "LinkManager layer slug lookup failed for layer 'pisa'")
        self.assertEqual(Link.objects.layer(2).count(), 0, "LinkManager layer id lookup failed for layer 'pisa'")