"""
nodeshot.core.links unit tests
"""

import simplejson as json

from django.core.exceptions import ValidationError

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures
from nodeshot.networking.net.models import Interface

from .models import Link
from .choices import LINK_STATUS, LINK_TYPE


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
        'test_ip_addresses.json'
    ]
    
    def setUp(self):
        l = Link()
        l.interface_a = Interface.objects.find(2)
        l.interface_b = Interface.objects.find(3)
        l.type = LINK_TYPE.get('radio')
        l.status = LINK_STATUS.get('active')
        self.link = l
    
    def test_non_radio_shouldnt_have_radio_info(self):
        """ *** A link of any type which is not "radio" should not have dBm or noise data *** """
        link = self.link
        link.dbm = -70
        link.noise = -90
        self.assertRaises(ValidationError, link.full_clean)
    
    def test_save_radio_link(self):
        """ *** It should be possible to save a new link *** """
        l = self.link
        l.type = LINK_TYPE.get('radio')
        l.dbm = -70
        l.noise = -90
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
    
    def test_node_name_properties(self):
        link = self.link
        link.interface_b = Interface.objects.find(3)  # different node
        self.assertIsNone(link.node_a_name)
        self.assertIsNone(link.node_b_name)
        link.save()
        link = Link.objects.find(link.id)
        self.assertEqual(link.node_a_name, link.node_a.name)
        self.assertEqual(link.node_b_name, link.node_b.name)
    
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
        self.assertEqual(link.type, LINK_TYPE.get('radio'))