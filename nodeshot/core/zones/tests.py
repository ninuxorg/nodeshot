"""
nodeshot.core.zones unit tests
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from nodeshot.core.zones.models import Zone

class ZoneTest(TestCase):
    
    fixtures = ['groups.json', 'test_users.json', 'test_zones.json', 'test_nodes.json']
    
    def setUp(self):
        z = Zone()
        z.name = 'test zone'
        z.time_zone = 'GMT+1'
        z.slug = 'test-zone'
        z.lat = '10'
        z.lng = '10'
        z.zoom = '12'
        z.organization = 'ninux.org'
        self.zone = z
    
    #def test_email_filled(self):
    #    """ *** Either an email or some mantainers should be set *** """
    #    self.assertRaises(ValidationError, self.zone.full_clean)
    
    def test_external_cant_have_parent(self):
        """ *** External zones cannot have parents *** """
        self.zone.is_external = True
        self.zone.parent = Zone.objects.get(pk=1)
        self.assertRaises(ValidationError, self.zone.full_clean)
    
    def test_parent_is_not_external(self):
        """ *** Zones cannot have parents which are flagged as "external" *** """
        self.zone.is_external = False
        self.zone.parent = Zone.objects.filter(is_external=True)[0]
        self.assertRaises(ValidationError, self.zone.full_clean)
