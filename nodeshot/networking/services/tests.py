import simplejson as json

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from nodeshot.core.base.tests import BaseTestCase
from nodeshot.core.base.tests import user_fixtures


class ServiceTest(BaseTestCase):
    
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
        'test_services.json'
    ]
    
    def test_api_service_category_list(self):
        # GET: 200 - service category list
        url = reverse('api_service_category_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
    def test_api_service_category_details(self):
        # GET: 200 - service category detail
        url = reverse('api_service_category_details', args=[1])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_api_service_list(self):
        # GET: 200 - service list
        url = reverse('api_service_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
    def test_api_service_details(self):
        # GET: 200 - service detail
        url = reverse('api_service_details', args=[1])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
