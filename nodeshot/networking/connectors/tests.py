"""
nodeshot.networking.connectors unit tests
"""

import simplejson as json

from netengine.backends.ssh import OpenWRT
from netengine.exceptions import NetEngineError

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures

from .models import DeviceConnector


class ConnectorTest(BaseTestCase):
    
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
        self.client.login(username='admin', password='tester')
        self._create_connectors()
    
    def _create_connectors(self):
        c1 = DeviceConnector.objects.create(
            backend='netengine.backends.ssh.OpenWRT',
            node_id=1,
            config={
                'username': 'root',
                'password': 'test'
            },
            host='127.0.0.1'
        )
        self.c1 = c1
    
    def test_unicode(self):
        unicode(self.c1)
    
    def test_admin_changelist(self):
        url = reverse('admin:connectors_deviceconnector_changelist')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_admin_change(self):
        url = reverse('admin:connectors_deviceconnector_change', args=[self.c1.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_get_netengine_backend(self):
        NetEngineBackend = self.c1._get_netengine_backend()
        self.assertTrue(NetEngineBackend is OpenWRT)
    
    def test_build_netengine_arguments(self):
        arguments = self.c1._build_netengine_arguments()
        test_arguments = {
            'host': self.c1.host,
            'username': 'root',
            'password': 'test'
        }
        self.assertEqual(arguments, test_arguments)
        
        self.c1.port = 20200
        test_arguments['port'] = 20200
        arguments = self.c1._build_netengine_arguments()
        self.assertEqual(arguments, test_arguments)
        
        self.c1.config = {}
        self.c1.port = None
        arguments = self.c1._build_netengine_arguments()
        self.assertEqual(arguments, { 'host': self.c1.host })
    
    def test_get_netengine_arguments(self):
        c1 = self.c1
        self.assertEqual(c1._get_netengine_arguments(), ['username', 'password'])
        self.assertEqual(c1.AVAILABLE_CONFIG_KEYS, ['username', 'password'])
        self.assertEqual(c1._get_netengine_arguments(required=True), ['username', 'password'])
        self.assertEqual(c1.REQUIRED_CONFIG_KEYS, ['username', 'password'])
        
        c2 = DeviceConnector()
        c2.backend = 'netengine.backends.snmp.AirOS'
        self.assertEqual(c2._get_netengine_arguments(), ['community', 'agent'])
        self.assertEqual(c2.AVAILABLE_CONFIG_KEYS, ['community', 'agent'])
        self.assertEqual(c2._get_netengine_arguments(required=True), [])
        self.assertEqual(c2.REQUIRED_CONFIG_KEYS, [])
    
    def test_validation_ok(self):
        c2 = DeviceConnector()
        c2.backend = 'netengine.backends.Dummy'
        c2.node_id = self.c1.node_id
        c2.host = '127.0.0.1'
        c2.full_clean()
    
    def test_validate_backend(self):
        c1 = self.c1
        
        # wrong connector class
        original_class = c1.backend
        c1.backend = 'iam.very.wrong'
        try:
            c1._validate_backend()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertIn('iam.very.wrong', e.messages[0])
            self.assertEquals(len(e.messages), 1)
    
    def test_validate_config(self):
        # missing username and password
        c2 = DeviceConnector()
        c2.backend = 'netengine.backends.ssh.AirOS'
        c2.node_id = self.c1.node_id
        c2.host = '127.0.0.1'
        try:
            c2._validate_config()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertEquals(len(e.messages), 1)
            self.assertIn('username, password', e.messages[0])
        
        # missing password
        c2.config = { 'username': 'root' }
        try:
            c2._validate_config()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertEquals(len(e.messages), 1)
            self.assertIn('password', e.messages[0])
        
        # missing username
        c2.config = { 'password': 'test' }
        try:
            c2._validate_config()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertEquals(len(e.messages), 1)
            self.assertIn('username', e.messages[0])
        
        # nothing missing
        c2.config['username'] = 'test'
        c2._validate_config()