import simplejson as json

from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures
from nodeshot.core.nodes.models import Node

from .models import *


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
    
    def test_interface_data_ip_addresses(self):
        ip = Ip.objects.get(pk=1)
        ip.save()
        
        ip_addresses = ip.interface.data['ip_addresses'].replace(' ', '').split(',')
        self.assertEqual(len(ip_addresses), ip.interface.ip_set.count())
        
        for ip in ip.interface.ip_set.all():
            self.assertIn(str(ip.address), ip_addresses)
    
    def test_device_manager(self):
        self.assertEqual(
            list(Device.objects.access_level_up_to('public').filter(location__distance_gte=(Point(41, 12), 8000))),
            list(Device.objects.filter(access_level__lte=0, location__distance_gte=(Point(41, 12), 8000)))
        )
    
    def test_netacl_manager(self):
        self.assertEqual(
            list(Ip.objects.access_level_up_to('public').filter(address__net_contained='172.16.40.0/24')),
            list(Ip.objects.filter(access_level__lte=0, address__net_contained='172.16.40.0/24'))
        )
    
    def test_device_inherits_node_location(self):
        """ ensure device location defaults to node location if empty """
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.location, d.node.geometry)
    
    def test_device_inherits_node_point(self):
        """ ensure device location defaults to node location if empty """
        node = Node.objects.get(pk=1)
        node.geometry = GEOSGeometry("POLYGON((12.501664825436 41.900427664574,12.524409957883 41.897552804356,12.53925866699 41.886499358789,12.495828338623 41.871289758828,12.478318878173 41.891611016451,12.502179809565 41.900810969491,12.501664825436 41.900427664574))")
        node.save()
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.location, d.node.point)
    
    def test_device_inherits_node_elevation(self):
        """ ensure device elevation is inherithed from node """
        d = Device.objects.create(name='test_device_location', node_id=1, type='radio')
        self.assertEqual(d.elev, d.node.elev)
    
    def test_shortcuts(self):
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
        user_1 = User.objects.get(pk=1)
        self.assertEqual(len(response.data['results']), Device.objects.accessible_to(user_1).count())
    
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
        
        # login as non-owner
        self.client.login(username='pisano', password='tester')
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
        user_1 = User.objects.get(pk=1)
        self.assertEqual(len(response.data['results']), Device.objects.filter(node_id=node.id).accessible_to(user_1).count())
    
    def test_device_creation_api_permissions(self):
        """ create device permissions: only node owner or admins can add devices """
        # non owner can only read
        node = Node.objects.get(pk=7)
        url = reverse('api_node_devices', args=[node.slug])
        
        device_data = {
            "name": "device creation test",
            "type": "radio",
            "description": "device creation test",
            "data": { "is_unittest": "true" }
        }
        
        # unauthenticated can't create
        response = self.client.post(url, device_data)
        self.assertEqual(response.status_code, 403)
        
        # login as non-owner
        self.client.login(username='pisano', password='tester')
        response = self.client.post(url, json.dumps(device_data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        # login as node owner
        self.client.login(username=node.owner.username, password='tester')
        
        # node owner can create device
        response = self.client.post(url, json.dumps(device_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], 'device creation test')
        self.assertEqual(response.data['data']['is_unittest'], 'true')
        # check DB
        device = Device.objects.order_by('-id').all()[0]
        self.assertEqual(device.description, 'device creation test')
        self.assertEqual(device.data['is_unittest'], 'true')
        device.delete()
        
        # admin can create device too
        self.client.logout()
        self.client.login(username='admin', password='tester')
        device_data["data"] = json.dumps(device_data["data"])
        response = self.client.post(url, device_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], 'device creation test')
        self.assertEqual(response.data['data']['is_unittest'], 'true')
        # check DB
        device = Device.objects.order_by('-id').all()[0]
        self.assertEqual(device.description, 'device creation test')
        self.assertEqual(device.data['is_unittest'], 'true')
    
    def test_interface_shortcuts(self):
        ethernet = Ethernet.objects.create(
            device_id=1,
            name='eth0',
            mac='00:27:22:38:13:f4',
            standard='fast',
            duplex='full'
        )
        self.assertEqual(ethernet.shortcuts['user'], ethernet.device.node.user)
        self.assertEqual(ethernet.owner, ethernet.device.node.user)
        self.assertEqual(ethernet.shortcuts['layer'], ethernet.device.node.layer)
        self.assertEqual(ethernet.layer, ethernet.device.node.layer)
        self.assertEqual(ethernet.shortcuts['node'], ethernet.device.node)
        self.assertEqual(ethernet.node, ethernet.device.node)
    
    def test_device_ethernet_api(self):
        """ API device ethernet interfaces """
        
        url = reverse('api_device_ethernet', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
        url = reverse('api_device_ethernet', args=[99])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_mac_address_rest_field(self):
        data = {
            "name": "eth0",
            "mac": "IAM WRONG",
            "tx_rate": 10000, 
            "rx_rate": 10000, 
            "data": {
                "status": "active"
            },
            "standard": "fast", 
            "duplex": "full"
        }
        self.client.login(username='romano', password='tester')
        url = reverse('api_device_ethernet', args=[2])
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['mac'][0], 'Invalid mac address')
        
        data['mac'] = '00:27:22:38:13:f4'
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    def test_device_ethernet_api_permissions(self):
        """ API device ethernet interfaces permissions to create """
        data = {
            "name": "eth0",
            "mac": "00:27:22:38:13:f4",
            "tx_rate": 10000, 
            "rx_rate": 10000, 
            "standard": "fast", 
            "duplex": "full",
            "data": { "status": "active" }
        }
        json_data = json.dumps(data)
        eth_count = Ethernet.objects.filter(device_id=2).count()
        url = reverse('api_device_ethernet', args=[2])
        
        # unlogged can't create
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Ethernet.objects.filter(device_id=2).count(), eth_count)
        
        # non-owner can't create
        self.client.login(username='registered', password='tester')
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Ethernet.objects.filter(device_id=2).count(), eth_count)
        self.client.logout()
        
        # owner can create
        self.client.login(username='romano', password='tester')
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ethernet.objects.filter(device_id=2).count(), eth_count+1)
        self.client.logout()
        Ethernet.objects.get(mac='00:27:22:38:13:f4').delete()
        
        # admin can create too
        self.client.login(username='admin', password='tester')
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ethernet.objects.filter(device_id=2).count(), eth_count+1)
    
    def test_device_ethernet_api_ACL(self):
        """ API device ethernet ACL """
        ethernet = Ethernet.objects.create(
            device_id=1,
            access_level=1,
            name='private',
            mac='00:27:22:38:13:a4',
            standard='fast',
            duplex='full'
        )
        
        url = reverse('api_device_ethernet', args=[1])
        device_url = reverse('api_device_details', args=[1])
        
        # unauthenticated can see only 1 record
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['ethernet']), 1)
        
        # registered can see two
        self.client.login(username='registered', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['ethernet']), 2)
        
        # set to higher access level
        ethernet.access_level = 2
        ethernet.save()
        
        # now registed can see only 1
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['ethernet']), 1)
        
        # community can see two
        self.client.logout()
        self.client.login(username='community', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['ethernet']), 2)
    
    def test_ethernet_details_api_permissions(self):
        """ ethernet details permissions: only owner or admins can alter data """
        # non owner can only read
        url = reverse('api_ethernet_details', args=[1])
        response = self.client.patch(url, { 'name': 'eth2' })
        self.assertEqual(response.status_code, 403)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        
        # login as non-owner
        self.client.login(username='pisano', password='tester')
        response = self.client.patch(url, { 'name': 'eth2' })
        self.assertEqual(response.status_code, 403)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        
        # login as owner
        ethernet = Ethernet.objects.get(pk=1)
        self.client.login(username=ethernet.owner.username, password='tester')
        
        # owner can edit
        response = self.client.patch(url, { 'name': 'eth2' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'eth2')
        # check DB
        ethernet = Ethernet.objects.get(pk=1)
        self.assertEqual(ethernet.name, 'eth2')
        
        # admin can edit too
        self.client.logout()
        self.client.login(username='admin', password='tester')
        response = self.client.patch(url, { 'name': 'admineth2' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'admineth2')
        # check DB
        ethernet = Ethernet.objects.get(pk=1)
        self.assertEqual(ethernet.name, 'admineth2')
    
    def test_ethernet_details_api_ACL(self):
        """ ethernet details ACL """
        # non owner can only read
        ethernet = Ethernet.objects.get(pk=1)
        ethernet.access_level = 1
        ethernet.save()
        url = reverse('api_ethernet_details', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        self.client.login(username='registered', password='tester')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_device_wireless_api(self):
        """ API device wireless interfaces """
        
        url = reverse('api_device_wireless', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
        url = reverse('api_device_wireless', args=[99])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_device_wireless_api_ACL(self):
        """ API device wireless ACL """
        wireless = Wireless.objects.create(
            device_id=1,
            access_level=1,
            name='private',
            mac='00:27:22:38:13:a5',
            standard='802.11n'
        )
        
        url = reverse('api_device_wireless', args=[1])
        device_url = reverse('api_device_details', args=[1])
        
        # unauthenticated can see 1
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['wireless']), 1)
        
        # registered can see 2
        self.client.login(username='registered', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['wireless']), 2)
        
        # set to higher access level
        wireless.access_level = 2
        wireless.save()
        
        # now registed can see only 1
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['wireless']), 1)
        
        # community can see two
        self.client.logout()
        self.client.login(username='community', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        # check device detail url too
        response = self.client.get(device_url)
        self.assertEqual(len(response.data['wireless']), 2)
    
    def test_device_wireless_api_permissions(self):
        """ API device wireless interfaces permissions to create """
        data = {
            "name": "ath0",
            "mac": "00:27:22:38:13:c4",
            "tx_rate": 10000, 
            "rx_rate": 10000, 
            "standard": "802.11n",
            "data": { "status": "active" }
            
        }
        json_data = json.dumps(data)
        eth_count = Wireless.objects.filter(device_id=2).count()
        url = reverse('api_device_wireless', args=[2])
        
        # unlogged can't create
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Wireless.objects.filter(device_id=2).count(), eth_count)
        
        # non-owner can't create
        self.client.login(username='registered', password='tester')
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Wireless.objects.filter(device_id=2).count(), eth_count)
        self.client.logout()
        
        # owner can create
        self.client.login(username='romano', password='tester')
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Wireless.objects.filter(device_id=2).count(), eth_count+1)
        self.client.logout()
        Wireless.objects.get(mac='00:27:22:38:13:c4').delete()
        
        # admin can create too
        self.client.login(username='admin', password='tester')
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Wireless.objects.filter(device_id=2).count(), eth_count+1)
    
    def test_wireless_details_api_permissions(self):
        """ wireless details permissions: only owner or admins can alter data """
        # non owner can only read
        url = reverse('api_wireless_details', args=[2])
        response = self.client.patch(url, { 'name': 'eth2' })
        self.assertEqual(response.status_code, 403)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        
        # login as non-owner
        self.client.login(username='pisano', password='tester')
        response = self.client.patch(url, { 'name': 'eth2' })
        self.assertEqual(response.status_code, 403)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        
        # login as owner
        wireless = Wireless.objects.get(pk=2)
        self.client.login(username=wireless.owner.username, password='tester')
        
        # owner can edit
        response = self.client.patch(url, { 'name': 'eth2' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'eth2')
        # check DB
        wireless = Wireless.objects.get(pk=2)
        self.assertEqual(wireless.name, 'eth2')
        
        # admin can edit too
        self.client.logout()
        self.client.login(username='admin', password='tester')
        response = self.client.patch(url, { 'name': 'admineth2' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'admineth2')
        # check DB
        wireless = Wireless.objects.get(pk=2)
        self.assertEqual(wireless.name, 'admineth2')
    
    def test_wireless_details_api_ACL(self):
        """ wireless details ACL """
        # non owner can only read
        wireless = Wireless.objects.get(pk=2)
        wireless.access_level = 1
        wireless.save()
        url = reverse('api_wireless_details', args=[2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        self.client.login(username='registered', password='tester')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_interface_ip_address_get(self):
        # GET 404
        response = self.client.get(reverse('api_interface_ip', args=[99]))
        self.assertEqual(response.status_code, 404)
        
        # GET 200
        response = self.client.get(reverse('api_interface_ip', args=[1]))
        self.assertEqual(response.status_code, 200)
    
    def test_interface_ip_address_post_and_permissions(self):
        url = reverse('api_interface_ip', args=[1])
        data = {
            "address": "10.40.0.35",
            "netmask": "10.40.0.0/24"
        }
        
        # POST 403 unauthenticated
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        
        # POST 403 non owner can't add ip
        self.client.login(username='pisano', password='tester')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        # POST 200 owner can add ip
        self.client.login(username=Interface.objects.find(1).owner.username, password='tester')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        # ensure address
        ip = Ip.objects.last()
        self.assertEqual(ip.address.__str__(), '10.40.0.35')
        ip.delete()
        self.client.logout()
        
        # POST 200 also admin can add ip
        self.client.login(username='admin', password='tester')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        # ensure address
        ip = Ip.objects.last()
        self.assertEqual(ip.address.__str__(), '10.40.0.35')
    
    def test_interface_ip_address_fields_validation(self):
        url = reverse('api_interface_ip', args=[1])
        data = {
            "address": "WRONG",
            "netmask": "VERY WRONG"
        }
        
        self.client.login(username=Interface.objects.find(1).owner.username, password='tester')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['address'][0], 'Invalid ip address')
        self.assertEqual(response.data['netmask'][0], 'Invalid ip network')
        
        data = {
            "address": "10.40.0.1",
            "netmask": "10.40."
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        
        data = {
            "address": "10.40.0.",
            "netmask": "10.40.0.0/24"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
    
    def test_interface_ip_api_ACL(self):
        url = reverse('api_interface_ip', args=[1])
        
        # non owner can only read
        interface = Interface.objects.get(pk=1)
        ip_count = interface.ip_set.count()
        ip = interface.ip_set.first()
        ip.access_level = 1
        ip.save()
        response = self.client.get(url)
        self.assertEqual(len(response.data), interface.ip_set.access_level_up_to('public').count())
        self.assertEqual(len(response.data), ip_count-1)
        
        self.client.login(username='registered', password='tester')
        response = self.client.get(url)
        self.assertEqual(len(response.data), interface.ip_set.access_level_up_to('registered').count())
        self.assertEqual(len(response.data), ip_count)
    
    def test_ip_address_details_permissions(self):
        url = reverse('api_ip_details', args=[1])
        data = json.dumps({
            "address": "10.40.0.35",
            "netmask": "10.40.0.0/24"
        })
        
        # PUT 403 unauthenticated
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        
        # PUT 403 non owner can't edit ip
        self.client.login(username='pisano', password='tester')
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        # PUT 200 owner can edit ip
        self.client.login(username=Ip.objects.find(1).owner.username, password='tester')
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # ensure address
        ip = Ip.objects.find(1)
        self.assertEqual(ip.address.__str__(), '10.40.0.35')
        self.client.logout()
        
        # PUT 200 also admin can edit ip
        self.client.login(username='admin', password='tester')
        data = json.dumps({
            "address": "10.40.0.36",
            "netmask": "10.40.0.0/24"
        })
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # ensure address
        ip = Ip.objects.find(1)
        self.assertEqual(ip.address.__str__(), '10.40.0.36')
    
    def test_ip_details_api_ACL(self):
        # non owner can only read
        ip = Ip.objects.get(pk=1)
        ip.access_level = 1
        ip.save()
        url = reverse('api_ip_details', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        self.client.login(username='registered', password='tester')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_bridge_interfaces_validation(self):
        bridge = Bridge(device_id=1, mac='00:11:22:33:44:55', name='br0')
        bridge.save()
        
        # must bridge at least 2
        with self.assertRaises(ValidationError):
            bridge.interfaces.add(Interface.objects.find(1))
        
        bridge.interfaces.add(Interface.objects.find(1), Interface.objects.find(2))
        bridge.full_clean()
        
        # can't bridge different devices
        ethernet = Ethernet.objects.create(device_id=2, mac='00:00:22:33:44:55', name='br0')
        with self.assertRaises(ValidationError):
            bridge.interfaces.add(ethernet)
        
        # test add
        ethernet.device_id = 1
        ethernet.save()
        bridge.interfaces.add(ethernet)
        
        # can't bridge self
        with self.assertRaises(ValidationError):
            bridge.interfaces.add(bridge)
    
    def test_device_bridge_api(self):
        bridge = Bridge(device_id=1, mac='00:11:22:33:44:55', name='br0')
        bridge.save()
        bridge.interfaces.add(Interface.objects.find(1), Interface.objects.find(2))
        
        url = reverse('api_device_bridge', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('http://', response.data[0]['interfaces_links'][0])
        self.assertIn('http://', response.data[0]['interfaces_links'][1])
        bridge.delete()
        
        data = {
            "name": "br0test", 
            "mac": "00:11:22:33:44:55",
            "interfaces": []
        }
        
        # POST 403: unauthorized
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.client.login(username='pisano', password='tester')
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        # POST 400: missing interfaces
        self.client.login(username=bridge.owner.username, password='tester')
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data['interfaces'] = [1, 2]
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # POST 201
        bridge = Bridge.objects.last()
        self.assertEquals(bridge.name, 'br0test')
        self.assertEquals(bridge.mac, '00:11:22:33:44:55')
        self.assertEquals(bridge.interfaces.count(), 2)
        
        # POST 400: duplicate mac address
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_bridge_details_api(self):
        bridge = Bridge(device_id=1, mac='00:11:22:33:44:55', name='br0')
        bridge.save()
        bridge.interfaces.add(Interface.objects.find(1), Interface.objects.find(2))
        
        url = reverse('api_bridge_details', args=[bridge.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('http://', response.data['interfaces_links'][0])
        self.assertIn('http://', response.data['interfaces_links'][1])
        
        # PATCH 403 unauthenticated
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, 403)
        
        # PATCH 403 logged in as non owner
        self.client.login(username='pisano', password='tester')
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        # PATCH 200 logged in as owner
        self.client.login(username=bridge.owner.username, password='tester')
        response = self.client.patch(url, { 'name': 'brtest' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'brtest')
        
        # PATCH 400 empty interfaces
        response = self.client.patch(url, json.dumps({ 'interfaces': [] }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.client.logout()
        
        # PATCH 200 by admin
        self.client.login(username='admin', password='tester')
        response = self.client.patch(url, { 'name': 'admin' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'admin')
    
    # TODO: write tests for vlan, tunnel, vap