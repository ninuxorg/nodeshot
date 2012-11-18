from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import urllib2
from xml.dom import minidom
import simplejson


class BaseConverter:
    """ Base interoperability class that converts an XML file to JSON format and saves it in ''{{ MEDIA_ROOT }}/external/nodes/<zone_slug>.json'' """
    
    mandatory = ['url']
    
    def __init__(self, zone, *args, **kwargs):
        self.zone = zone
        self.config = simplejson.loads(zone.external.config)
        self.validate()
    
    def validate(self):
        for field in self.mandatory:
            if not self.config.get(field, False):
                raise ImproperlyConfigured('Mandatory %s parameter missing from configuration' % field)
    
    def process(self):
        """ this is the method that does everything automatically (at least attempts to) """
        self.retrieve_content()
        self.parse()
        json = self.convert_nodes()
        message = self.save_nodes(json)
        # return message as a list because more than one messages might be returned
        return [message]
    
    def retrieve_content(self):
        """ retrieve xml data """
        self.content = urllib2.urlopen(self.config.get('url')).read()
    
    def parse(self):
        """ parse XML data """
        self.parsed_content = minidom.parseString(self.content)
    
    def save_nodes(self, content):
        """ save node list file on server's hard drive """
        # convenience variables for readability
        file_name = '%s.json' % self.zone.slug
        file_contents = ContentFile(content)
        path = '%sexternal/nodes/%s' % (settings.MEDIA_ROOT, file_name)
        # delete file if already exists
        if default_storage.exists(path):
            default_storage.delete(path)
        # save file on disk
        file = default_storage.save(path, file_contents)
        # return message
        return 'JSON file saved in "%s"' % path
    
    @staticmethod
    def get_text(item, tag):
        """ returns text content of an xml tag """
        xmlnode = item.getElementsByTagName(tag)[0].firstChild
        if xmlnode is not None:
            return unicode(xmlnode.nodeValue)
        # empty tag
        else:
            return ''