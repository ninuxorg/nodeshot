from django.core.exceptions import ImproperlyConfigured
import simplejson as json
import urllib2


class ProvinciaWIFI:
    """ ProvinciaWIFI interoperability class"""
    
    mandatory = ['url']
    
    def __init__(self, config, *args, **kwargs):
        self.config = json.loads(config)
        self.validate()
        self.process()
    
    def validate(self):
        for field in self.mandatory:
            if not self.config.get(field, False):
                raise ImproperlyConfigured('Mandatory %s parameter missing from configuration' % field)
    
    def process(self):
        pass
    
    def download_xml(self):
        pass