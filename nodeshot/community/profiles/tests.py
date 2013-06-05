"""
ndoeshot.contrib.profiles tests
"""

from django.test import TestCase
from django.contrib.auth.models import User

from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.models.choices import NODE_STATUS
from nodeshot.networking.net.models import Device

from models import Stats


class ProfilesTest(TestCase):
    
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
        self.fusolab = Node.objects.get(slug='fusolab')
    
    def test_potential_nodes(self):
        """ potential nodes basic count test """
        self.assertEqual(self.fusolab.user.stats.potential_nodes, 1)
    
    def test_active_nodes(self):
        """ active nodes basic count test """
        self.assertEqual(self.fusolab.user.stats.active_nodes, 3)    
    
    #def test_hotspots(self):
    #    """ potential nodes basic count test """
    #    self.assertEqual(self.fusolab.user.stats.hotspots, 1)
    
    def test_devices(self):
        """ potential nodes basic count test """
        self.assertEqual(self.fusolab.user.stats.devices, 2)
    
    def test_create_test_obj_on_save(self):
        """ if for some reason a stats object does not exist it should be created with update_or_create """
        self.fusolab.user.stats.delete()
        # retrieve from DB again
        self.fusolab = Node.objects.get(slug='fusolab')
        try:
            stats = self.fusolab.user.stats
        except Stats.DoesNotExist:
            stats = None
        self.assertEqual(stats, None, 'should be None')
        old_desc = self.fusolab.description
        self.fusolab.description = '%s + changed' % old_desc
        self.fusolab.save()
        self.assertEqual(self.fusolab.description, '%s + changed' % old_desc)
    
    def test_node_count_change(self):
        """ when a new node is added nodes count should be updated """
        new_node = Node(user_id=4, name='new node', slug='new_node', layer_id=1, coords="POINT (41.9720419277 12.5822391919)")
        new_node.save()
        self.assertEqual(new_node.user.stats.potential_nodes, 2, "Potential nodes increment count failed")
        new_node.status = NODE_STATUS.get('active')
        new_node.save()
        self.assertEqual(new_node.user.stats.active_nodes, 4, "Active nodes increment count failed")
        self.assertEqual(new_node.user.stats.potential_nodes, 1, "Potential nodes decrement count failed")
        #new_node.is_hotspot = True
        #new_node.save()
        #self.assertEqual(new_node.user.stats.hotspots, 2, "Hotspot increment count failed")
        new_node.delete()
        user = User.objects.get(username='romano')
        self.assertEqual(user.stats.active_nodes, 3, "Active nodes decrement count failed")
        #self.assertEqual(user.stats.hotspots, 1, "Hotspot decrement count failed")
    
    def test_device_count_change(self):
        """ when a device is added or deleted stats should change """
        new_device = Device(node_id=1, name='new device', type='radio')
        new_device.save()
        self.assertEqual(new_device.node.user.stats.devices, 3, "Device increment count failed")
        new_device.delete()
        user = User.objects.get(username='romano')
        self.assertEqual(user.stats.devices, 2, "Device decrement count failed")
    
    def test_new_users_have_default_group(self):
        """ users should have a default group when created """
        new_user = User(username='tester', password='tester', email='tester@test.com')
        new_user.save()
        self.assertEqual(new_user.groups.filter(name='registered').count(), 1, "default user group fail")

    def test_new_users_should_generate_onetoones(self):
        """ users should have a default group when created """
        new_user = User(username='tester', password='tester', email='tester@test.com')
        new_user.save()
        self.assertEqual(new_user.stats.active_nodes, 0, "new user stats fail")
        self.assertEqual(new_user.emailnotification.new_potential_node, True, "new user email notification settings fail")
        self.assertEqual(new_user.profile.__unicode__(), 'tester', "new user profile fail")