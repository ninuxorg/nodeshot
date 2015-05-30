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
from nodeshot.networking.net.models import *

from .models import DeviceConnector
from . import settings

settings.NETENGINE_BACKENDS += [('netengine.backends.Dummy', 'Dummy')]


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
        self.c1 = DeviceConnector.objects.create(backend='netengine.backends.Dummy',
                                                 node_id=1,
                                                 host='127.0.0.1')

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

    def test_saved_data(self):
        c1 = self.c1
        self.assertEquals(c1.device.name, 'dummy')
        self.assertEquals(c1.device.os, 'dummyOS')
        self.assertEquals(c1.device.interface_set.count(), 2)

        # ensure a new routing protocol has been created
        rp_count = RoutingProtocol.objects.filter(name='olsr', version='dummy version').count()
        self.assertEquals(rp_count, 1)

        # ensure vap interfaces have been created
        wireless = Wireless.objects.filter(device=c1.device)[0]
        self.assertEquals(wireless.vap_set.count(), 1)

    def test_get_netengine_backend(self):
        self.c1.backend = 'netengine.backends.ssh.OpenWRT'
        NetEngineBackend = self.c1._get_netengine_backend()
        self.assertTrue(NetEngineBackend is OpenWRT)

    def test_build_netengine_arguments(self):
        c1 = DeviceConnector(
            backend='netengine.backends.ssh.OpenWRT',
            host='127.0.0.1',
            config = {
                'username': 'root',
                'password':'test'
            }
        )
        arguments = c1._build_netengine_arguments()
        test_arguments = {
            'host': self.c1.host,
            'username': 'root',
            'password': 'test'
        }
        self.assertEqual(arguments, test_arguments)

        c1.port = 20200
        test_arguments['port'] = 20200
        arguments = c1._build_netengine_arguments()
        self.assertEqual(arguments, test_arguments)

        c1.config = {}
        c1.port = None
        arguments = c1._build_netengine_arguments()
        self.assertEqual(arguments, { 'host': self.c1.host })

    def test_get_netengine_arguments(self):
        c1 = DeviceConnector(
            backend='netengine.backends.ssh.OpenWRT',
            host='127.0.0.1',
            config = {
                'username': 'root',
                'password':'test'
            }
        )
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
        self.c1.device.delete()
        self.c1.delete()
        c2 = DeviceConnector()
        c2.backend = 'netengine.backends.Dummy'
        c2.node_id = self.c1.node_id
        c2.host = '127.0.0.1'
        c2.full_clean()
        c2.save()

    def test_validate_backend(self):
        # wrong connector class
        c1 = DeviceConnector(backend='iam.very.wrong',
                             node_id=1,
                             host='127.0.0.1')
        try:
            c1._validate_backend()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertIn('iam.very.wrong', e.messages[0])
            self.assertEquals(len(e.messages), 1)

    def test_validate_config_missing_keys(self):
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

    def test_validate_config_unrecognized_keys(self):
        c2 = DeviceConnector()
        c2.backend = 'netengine.backends.ssh.AirOS'
        c2.node_id = self.c1.node_id
        c2.host = '127.0.0.1'

        # unrecoginzed parameter "wrong"
        c2.config = {
            'username': 'user',
            'password': 'test',
            'wrong': 'wrong'
        }
        try:
            c2._validate_config()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertEquals(len(e.messages), 1)
            self.assertIn('wrong', e.messages[0])

        # no unrecognized keys
        c2.config.pop('wrong')
        c2._validate_config()

    def test_validate_netengine(self):
        c1 = DeviceConnector(
            backend='netengine.backends.ssh.AirOS',
            host='192.168.1.254',
            config = {
                'username': 'user',
                'password':'test'
            }
        )
        # expect connection error
        with self.assertRaises(ValidationError):
            c1._validate_netengine()

    def test_validate_duplicates(self):
        dup = DeviceConnector(backend='netengine.backends.Dummy',
                              node_id=1,
                              host='127.0.0.1')

        try:
            dup._validate_duplicates()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertEquals(len(e.messages), 1)
            self.assertIn('de:9f:db:30:c9:c4', e.messages[0])
            self.assertIn('de:9f:db:30:c9:c5', e.messages[0])
