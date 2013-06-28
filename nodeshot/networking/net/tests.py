from django.test import TestCase
from .models import Ip

from nodeshot.core.base.tests import user_fixtures


class NetworkModelTest(TestCase):
    """
    Network Model Tests
    """
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
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
