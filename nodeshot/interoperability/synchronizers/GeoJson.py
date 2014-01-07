import simplejson as json

from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.conf import settings

from nodeshot.core.nodes.models import Node, Status

from .base import BaseConverter, HttpRetrieverMixin



class GeoJson(HttpRetrieverMixin, BaseConverter):
    """ GeoJSON synchronizer """
    
    REQUIRED_CONFIG_KEYS = [
        'url',
        'map',
    ]
    
    def parse(self):
        """ retrieve data """
        try:
            self.data = json.loads(self.data)
        except Exception as e:
            raise Exception('Error while converting response from JSON to python. %s' % e)
        
        if self.data.get('type', '') != 'FeatureCollection':
            raise Exception('GeoJson synchronizer expects a FeatureCollection object at root level')
    
    def save(self):
        """ synchronize DB """
        # retrieve all items
        items = self.data['features']
        
        # init empty lists
        added_nodes = []
        changed_nodes = []
        unmodified_nodes = []
        
        key_map = self.config.get('map')
        name_key = key_map.get('name', 'name')
        description_key = key_map.get('description', 'description')
        address_key = key_map.get('address', 'address')
        elevation_key = key_map.get('elevation', 'elev')
        
        # retrieve a list of all the slugs of this layer
        layer_nodes_slug_list = Node.objects.filter(layer=self.layer).values_list('slug', flat=True)
        # keep a list of all the nodes of other layers
        other_layers_slug_list = Node.objects.exclude(layer=self.layer).values_list('slug', flat=True)
        # init empty list of slug of external nodes that will be needed to perform delete operations
        processed_slug_list = []
        deleted_nodes_count = 0
        
        try:
            self.status = Status.objects.get(slug__iexact=self.config.get('status', ''))
        except Status.DoesNotExist:
            self.status = None
        
        # loop over every item
        for item in items:
            
            # name is required
            try:
                name = item['properties'][name_key]
            except KeyError:
                raise Exception('Expected property %s not found in item %s.' % (name_key, item))
            
            slug = slugify(name)
            
            number = 1
            original_name = name
            needed_different_name = False
            
            while True:
                # items might have the same name... so we add a number..
                if slug in processed_slug_list or slug in other_layers_slug_list:
                    needed_different_name = True
                    number = number + 1
                    name = "%s - %d" % (original_name, number)
                    slug = slug = slugify(name)                    
                else:
                    if needed_different_name:
                        self.verbose('needed a different name for %s, trying "%s"' % (original_name, name))
                    break
            
            description = item['properties'].get(description_key, '')
            address = item['properties'].get(address_key, '')
            elevation = item['properties'].get(elevation_key, None)
            
            # geometry
            geojson = json.dumps(item['geometry'])
            geometry = GEOSGeometry(geojson)
            
            # default values
            added = False
            changed = False
            
            try:
                # edit existing node
                node = Node.objects.get(slug=slug, layer=self.layer)
            except Node.DoesNotExist:
                # add a new node
                node = Node()
                node.layer = self.layer
                node.status = self.status
                added = True
            
            if node.name != name:
                node.name = name
                changed = True
            
            if node.slug != slug:
                node.slug = slug
                changed = True
            
            # TODO: this must be DRYed
            if added is True or (
                node.geometry.equals(geometry) is False and
                node.geometry.equals_exact(geometry) is False
                ):
                node.geometry = geometry
                changed = True
            
            if node.description != description:
                node.description = description
                changed = True
            
            if node.address != address:
                node.address = address
                changed = True
            
            if node.elev != elevation:
                node.elev = elevation
                changed = True
            
            # TODO: data
            
            # perform save or update only if necessary
            if added or changed:
                try:
                    node.full_clean()
                    node.save()
                except ValidationError as e:
                    # TODO: are we sure we want to interrupt the execution?
                    raise Exception("%s errors: %s" % (name, e.messages))
            
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
            processed_slug_list.append(node.slug)
        
        # delete old nodes
        for local_node in layer_nodes_slug_list:
            # if local node not found in external nodes
            if not local_node in processed_slug_list:
                node_name = node.name
                # retrieve from DB and delete
                node = Node.objects.get(slug=local_node)
                node.delete()
                # then increment count that will be included in message
                deleted_nodes_count = deleted_nodes_count + 1
                self.verbose('node "%s" deleted' % node_name)
        
        # message that will be returned
        self.message = """
            %s nodes added
            %s nodes changed
            %s nodes deleted
            %s nodes unmodified
            %s total external records processed
            %s total local nodes for this layer
        """ % (
            len(added_nodes),
            len(changed_nodes),
            deleted_nodes_count,
            len(unmodified_nodes),
            len(items),
            Node.objects.filter(layer=self.layer).count()
        )