from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node

from .models import *


class NetworkModelTest(TestCase):
    """
    Network Model Tests
    """
    
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
    
    def test_ip_automatic_protocol_detection(self):
        """ automatic protocol detection """
        ip = Ip.objects.get(pk=1)
        ip.save()
        self.assertEquals('ipv4', ip.protocol)
        
        ip = Ip.objects.get(pk=2)
        ip.save()
        self.assertEquals('ipv6', ip.protocol)
    
    def test_device_inherits_node_location(self):
        """ ensure device location defaults to node location if empty """
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.location, d.node.geometry)
    
    def test_device_inherits_node_geometry_centroid(self):
        """ ensure device location defaults to node location if empty """
        node = Node.objects.get(pk=1)
        node.geometry = GEOSGeometry("POLYGON((12.501664825436 41.900427664574,12.524409957883 41.897552804356,12.53925866699 41.886499358789,12.495828338623 41.871289758828,12.478318878173 41.891611016451,12.502179809565 41.900810969491,12.501664825436 41.900427664574))")
        node.save()
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.location, d.node.geometry.centroid)
    
    def test_device_inherits_node_elevation(self):
        """ ensure device elevation is inherithed from node """
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.elev, d.node.elev)
    
    def test_shortcuts(self):
        """ assuming HSTORE is enabled """
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.shortcuts['user'], d.node.user)
        self.assertEqual(d.owner, d.node.user)
        self.assertEqual(d.shortcuts['layer'], d.node.layer)
        self.assertEqual(d.layer, d.node.layer)