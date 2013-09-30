import requests
import simplejson as json

from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.conf import settings

from nodeshot.core.nodes.models import Node, Status

from .base import BaseConverter

if settings.NODESHOT['SETTINGS'].get('HSTORE', False) is False:
    raise ImproperlyConfigured('HSTORE needs to be enabled for ProvinciaWIFI Converter to work properly')



class ProvinciaBorders(BaseConverter):
    """ ProvinciaBorders interoperability class """
    
    def retrieve_data(self):
        """ retrieve data """
        # shortcuts for readability
        comuni_borders_url = self.config.get('comuni_borders_url')
        provincia_borders_url = self.config.get('provincia_borders_url')

        verify_SSL = self.config.get('verify_SSL', True)
        
        # do HTTP request and store content
        self.comuni = requests.get(comuni_borders_url, verify=verify_SSL).content
        self.provincia = requests.get(provincia_borders_url, verify=verify_SSL).content
    
    def parse(self):
        """ parse data """
        print("Parsing data...")
        self.comuni = json.loads(self.comuni)["features"]
        self.provincia = json.loads(self.provincia)["features"]
        print("Parsed data...")
    def save(self):
        """ synchronize DB """
        self.process_borders(self.provincia)
        self.process_borders(self.comuni)
    
    def process_borders(self,borders):
        if not borders:
            self.message = """
            Borders data not processed.
            """
            return False
        # retrieve all items
        items = borders
        
        # init empty lists
        added_nodes = []
        changed_nodes = []
        unmodified_nodes = []
        
        # retrieve a list of local nodes in DB
        local_nodes_slug = Node.objects.filter(layer=self.layer).values_list('slug', flat=True)
        # init empty list of slug of external nodes that will be needed to perform delete operations
        external_nodes_slug = []
        deleted_nodes_count = 0
        
        try:
            self.status = Status.objects.get(slug=self.config.get('status', None))
        except Status.DoesNotExist:
            self.status = None
        
        # loop over every parsed item
        for item in items:
            # retrieve info in auxiliary variables
            # readability counts!
            name = item['properties'].get('name', '')[0:70]
            address = name
            slug = slugify(name)
            #print(slug)
            number = 1
            original_name = name
            needed_different_name = False
            
            while True:
                # items might have the same name... so we add a number..
                if slug in external_nodes_slug:
                    needed_different_name = True
                    number = number + 1
                    name = "%s - %d" % (original_name, number)
                    slug = slug = slugify(name)                    
                else:
                    if needed_different_name:
                        self.verbose('needed a different name for %s, trying "%s"' % (original_name, name))
                    break
            
            # geometry object
            geometry = GEOSGeometry(json.dumps(item["geometry"]))
            
            # default values
            added = False
            changed = False
            
            try:
                # edit existing node
                node = Node.objects.get(slug=slug)
            except Node.DoesNotExist:
                # add a new node
                node = Node()
                node.layer = self.layer
                node.status = self.status
                node.data = {}
                added = True
            
            if node.name != name:
                node.name = name
                changed = True
            
            if node.slug != slug:
                node.slug = slug
                changed = True
            
            if added is True or node.geometry.equals(geometry) is False:
                node.geometry = geometry
                changed = True
            
            if node.address != address:
                node.address = address
                changed = True
            
            # perform save or update only if necessary
            if added or changed:
                try:
                    node.full_clean()
                    node.save()
                except ValidationError as e:
                    # TODO: are we sure we want to interrupt the execution?
                    raise Exception("%s import errors: %s" % (name, e.messages))
            
            if added:
                added_nodes.append(node)
                self.verbose('new node saved with name "%s"' % node.name)
            elif changed:
                changed_nodes.append(node)
                self.verbose('node "%s" updated' % node.name)
            else:
                unmodified_nodes.append(node)
                self.verbose('node "%s" unmodified' % node.name)
            
            # fill node list container
            external_nodes_slug.append(node.slug)
        
        # delete old nodes
        for local_node in local_nodes_slug:
            # if local node not found in external nodes
            if not local_node in external_nodes_slug:
                node_name = node.name
                # retrieve from DB and delete
                node = Node.objects.get(slug=local_node)
                node.delete()
                # then increment count that will be included in message
                deleted_nodes_count = deleted_nodes_count + 1
                self.verbose('node "%s" deleted' % node_name)
        
        self.layer.external.config = json.dumps(self.config, indent=4, sort_keys=True)
        self.layer.external.save()
        
        # message that will be returned
        self.message = """
            %s node added
            %s node changed
            %s node deleted
            %s node unmodified
            %s total external records processed
            %s total local records for this layer
        """ % (
            len(added_nodes),
            len(changed_nodes),
            deleted_nodes_count,
            len(unmodified_nodes),
            len(items),
            Node.objects.filter(layer=self.layer).count()
        )