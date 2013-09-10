import requests
import simplejson as json
from xml.dom import minidom

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from nodeshot.core.base.utils import pause_disconnectable_signals, resume_disconnectable_signals
from nodeshot.core.nodes.models import Node


__all__ = [
    # classes
    'BaseConverter',
    'XMLConverter',
    
    # mixins
    'HttpRetrieverMixin',
    'XMLParserMixin',
    'JSONFileStorageMixin'
]


class BaseConverter(object):
    """ Base interoperability class that converts an XML file to JSON format and saves it in ''{{ MEDIA_ROOT }}/external/nodes/<layer_slug>.json'' """
    
    REQUIRED_CONFIG_KEYS = []
    
    def __init__(self, layer, *args, **kwargs):
        """
        :layer models.Model: instance of Layer we want to convert 
        """
        self.layer = layer
        self.verbosity = kwargs.get('verbosity', 1)
        self.config = json.loads(layer.external.config)
        self.validate()
    
    def validate(self):
        """ Ensure required config keys are present """
        for field in self.REQUIRED_CONFIG_KEYS:
            if not self.config.get(field, False):
                raise ImproperlyConfigured('Required %s parameter missing from configuration' % field)
    
    def process(self):
        """
        This is the method that does everything automatically (at least attempts to).
        
        Steps:
            1. Retrieve data from external source
            2. Parse the data
            3. Save the data locally
        """
        self.retrieve_data()
        self.parse()
        
        # TRICK: disable new_nodes_allowed_for_layer validation
        Node._additional_validation.remove('new_nodes_allowed_for_layer')
        # avoid sending zillions of notifications
        pause_disconnectable_signals()
        
        self.save()
        
        # Re-enable new_nodes_allowed_for_layer validation
        Node._additional_validation.insert(0, 'new_nodes_allowed_for_layer')
        # reconnect signals
        resume_disconnectable_signals()
        
        # return message as a list because more than one messages might be returned
        return [self.message]
    
    def retrieve_data(self):
        """ retrieve data """
        raise NotImplementedError("BaseConverter child class does not implement a retrieve_data method")
    
    def parse(self):
        """ parse data """
        raise NotImplementedError("BaseConverter child class does not implement a parse method")
    
    def save(self):
        """ save output file on server's hard drive """
        raise NotImplementedError("BaseConverter child class does not implement a save method")
    
    def verbose(self, message):
        if self.verbosity == 2:
            print(message)
    

class HttpRetrieverMixin(object):
    """ Retrieve external data through HTTP """
    
    def retrieve_data(self):
        """ retrieve data """
        # shortcuts for readability
        url = self.config.get('url')
        verify_SSL = self.config.get('verify_SSL', True)
        
        # do HTTP request and store content
        self.data = requests.get(url, verify=verify_SSL).content


class XMLParserMixin(object):
    """ XML Parsing utility methods """
    
    def parse(self):
        """ parse data """
        self.parsed_data = minidom.parseString(self.data)
    
    @staticmethod
    def get_text(item, tag):
        """ returns text content of an xml tag """
        xmlnode = item.getElementsByTagName(tag)[0].firstChild
        
        if xmlnode is not None:
            return unicode(xmlnode.nodeValue)
        # empty tag
        else:
            return ''


class JSONFileStorageMixin(object):
    """
    Mixin for saving a JSON file
    
    DEPRECATED
    """
    
    def save(self, resource_name='nodes'):
        """ save output file on server's hard drive """
        name = self.layer.slug
        content = self.parsed_data
        
        file_name = '%s.json' % name
        file_contents = ContentFile(content)
        path = '%sexternal/%s/%s' % (settings.MEDIA_ROOT, resource_name, file_name)
        
        # delete file if already exists
        if default_storage.exists(path):
            default_storage.delete(path)
            
        # save file on disk
        file = default_storage.save(path, file_contents)
        
        # message that will be returned
        self.message = 'JSON file saved in "%s"' % path


class XMLConverter(HttpRetrieverMixin, XMLParserMixin, BaseConverter):
    """ XML HTTP converter """
    
    REQUIRED_CONFIG_KEYS = ['url']