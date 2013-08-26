import simplejson as json

from django.contrib.gis.geos import GEOSGeometry
from django.core.urlresolvers import reverse
from django.conf import settings

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node

from .models import *

HSTORE_ENABLED = settings.NODESHOT['SETTINGS'].get('HSTORE', True)


class NetTest(BaseTestCase):
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
    
    def test_device_list_api(self):
        """ API device list """
        url = reverse('api_device_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), Device.objects.access_level_up_to('public').count())
    
    def test_device_list_search_api(self):
        """ API device list search """
        url = reverse('api_device_list')
        response = self.client.get(url, { 'search': 'RDP' })
        self.assertEqual(len(response.data['results']), 1)
    
    def test_device_list_api_ACL(self):
        """ API device list ACL """
        device = Device.objects.get(pk=1)
        device.access_level = 2
        device.save()
        
        url = reverse('api_device_list')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), Device.objects.access_level_up_to('public').count())
        
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), Device.objects.accessible_to(1).count())
    
    def test_device_details_api(self):
        url = reverse('api_device_details', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_device_details_api_permissions(self):
        """ device detail permissions: only owner or admins can alter data """
        # non owner can only read
        url = reverse('api_device_details', args=[1])
        response = self.client.patch(url, { 'description': 'permission test' })
        self.assertEqual(response.status_code, 403)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        
        # login as owner
        device = Device.objects.get(pk=1)
        self.client.login(username=device.owner.username, password='tester')
        
        # owner can edit
        response = self.client.patch(url, { 'description': 'permission test' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'permission test')
        # check DB
        device = Device.objects.get(pk=1)
        self.assertEqual(device.description, 'permission test')
        
        # admin can edit too
        self.client.logout()
        self.client.login(username='admin', password='tester')
        response = self.client.patch(url, { 'description': 'i am the admin' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'i am the admin')
        # check DB
        device = Device.objects.get(pk=1)
        self.assertEqual(device.description, 'i am the admin')
    
    def test_node_device_list_api(self):
        """ API node device list """
        
        url = reverse('api_node_devices', args=[Node.objects.get(pk=7).slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        
        url = reverse('api_node_devices', args=['idontexist'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_node_device_list_api_ACL(self):
        """ API device list ACL """
        device = Device.objects.get(pk=1)
        device.access_level = 2
        device.save()
        
        node = Node.objects.get(pk=7)
        url = reverse('api_node_devices', args=[node.slug])
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), Device.objects.filter(node_id=node.id).access_level_up_to('public').count())
        
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), Device.objects.filter(node_id=node.id).accessible_to(1).count())
    
    def test_device_creation_api_permissions(self):
        """ create device permissions: only node owner or admins can add devices """
        # non owner can only read
        node = Node.objects.get(pk=7)
        url = reverse('api_node_devices', args=[node.slug])
        
        device_data = {
            "name": "device creation test",
            "type": "radio",
            "description": "device creation test",
        }
        
        if HSTORE_ENABLED:
            device_data["data"] = { "is_unittest": "true" }
        
        response = self.client.post(url, device_data)
        self.assertEqual(response.status_code, 403)
        
        # login as node owner
        self.client.login(username=node.owner.username, password='tester')
        
        # node owner can create device
        response = self.client.post(url, json.dumps(device_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], 'device creation test')
        if HSTORE_ENABLED:
            self.assertEqual(response.data['data']['is_unittest'], 'true')
        # check DB
        device = Device.objects.order_by('-id').all()[0]
        self.assertEqual(device.description, 'device creation test')
        if HSTORE_ENABLED:
            self.assertEqual(device.data['is_unittest'], 'true')
        device.delete()
        
        # admin can create device too
        self.client.logout()
        self.client.login(username='admin', password='tester')
        device_data["data"] = json.dumps(device_data["data"])
        response = self.client.post(url, device_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], 'device creation test')
        if HSTORE_ENABLED:
            self.assertEqual(response.data['data']['is_unittest'], 'true')
        # check DB
        device = Device.objects.order_by('-id').all()[0]
        self.assertEqual(device.description, 'device creation test')
        if HSTORE_ENABLED:
            self.assertEqual(device.data['is_unittest'], 'true')