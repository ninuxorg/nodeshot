import requests
import simplejson
from xml.dom import minidom

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class BaseConverter(object):
    """ Base interoperability class that converts an XML file to JSON format and saves it in ''{{ MEDIA_ROOT }}/external/nodes/<layer_slug>.json'' """
    
    mandatory = ['url']
    
    def __init__(self, layer, *args, **kwargs):
        self.layer = layer
        self.config = simplejson.loads(layer.external.config)
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
        message = self.save_file(self.layer.slug, json)
        # return message as a list because more than one messages might be returned
        return [message]
    
    def retrieve_content(self):
        """ retrieve data """
        # shortcuts for readability
        url = self.config.get('url')
        verify_SSL = self.config.get('verify_SSL', True)
        # do HTTP request and store content
        self.content = requests.get(url, verify=verify_SSL).content
    
    def parse(self):
        """ parse data """
        self.parsed_content = minidom.parseString(self.content)
    
    def save_file(self, name, content, resource_name='nodes'):
        """ save output file on server's hard drive """
        file_name = '%s.json' % name
        file_contents = ContentFile(content)
        path = '%sexternal/%s/%s' % (settings.MEDIA_ROOT, resource_name, file_name)
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