import simplejson as json

from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.nodes.models import Node, Status

from .base import BaseSynchronizer, HttpRetrieverMixin



class GeoJson(HttpRetrieverMixin, BaseSynchronizer):
    """ GeoJSON synchronizer """
    
    REQUIRED_CONFIG_KEYS = [
        'url',
        'map',
    ]
    
    def parse(self):
        """ parse geojson and ensure is collection """
        try:
            self.data = json.loads(self.data)
        except Exception as e:
            raise Exception('Error while converting response from JSON to python. %s' % e)
        
        if self.data.get('type', '') != 'FeatureCollection':
            raise Exception('GeoJson synchronizer expects a FeatureCollection object at root level')
    
    def parse_item(self, item):
        result = {
            "name": item['properties'].pop(self.keys['name'], ''),
            "status": item['properties'].pop(self.keys['status'], None),
            "address": item['properties'].pop(self.keys['address'], ''),
            "is_published": item['properties'].pop(self.keys['is_published'], True),
            "user": item['properties'].pop(self.keys['user'], None),
            "geometry": GEOSGeometry(json.dumps(item['geometry'])),
            "elev": item['properties'].pop(self.keys['elev'], None),
            "description": item['properties'].pop(self.keys['description'], ''),
            "notes": item['properties'].pop(self.keys['notes'], ''),
            "data": {}
        }
        
        # loop over remainig items and put them into data dictionary
        for key, value in item['properties'].items():
            result["data"][key] = value
        
        return result
    
    def _convert_item(self, item):
        """
        take a parsed item as input and returns a python dictionary
        the keys will be saved into the Node model
        either in their respective fields or in the hstore "data" field
        
        :param item: object representing parsed item
        """
        item = self.parse_item(item)
        
        # name is required
        if not item['name']:
            raise Exception('Expected property %s not found in item %s.' % (self.keys['name'], item))
        
        if not item['status']:
            item['status'] = self.default_status
        
        # get status or get default status or None
        try:
            item['status'] = Status.objects.get(slug__iexact=item['status'])
        except Status.DoesNotExist:
            try:
                item['status'] = Status.objects.filter(is_default=True)[0]
            except IndexError:
                item['status'] = None
        
        # slugify slug
        item['slug'] = slugify(item['name'])
        
        if not item['address']:
            item['address'] = ''
        
        if not item['is_published']:
            item['is_published'] = ''
        
        # get user or None
        try:
            item['user'] = User.objects.get(username=item['user'])
        except User.DoesNotExist:
            item['user'] = None
        
        if not item['elev']:
            item['elev'] = None
        
        if not item['description']:
            item['description'] = ''
        
        if not item['notes']:
            item['notes'] = ''
        
        result = {
            "name": item['name'],
            "slug": item['slug'],
            "status": item['status'],
            "address": item['address'],
            "is_published": item['is_published'],
            "user": item['user'],
            "geometry": item['geometry'],
            "elev": item['elev'],
            "description": item['description'],
            "notes": item['notes'],
            "data": {}
        }
        
        # ensure all additional data items are strings
        for key, value in item['data'].items():
            result["data"][key] = str(value)
        
        return result
    
    def save(self):
        """
        save data into DB:
        
         1. save new (missing) data
         2. update only when needed
         3. delete old data
         4. generate report that will be printed
        
        constraints:
         * ensure new nodes do not take a name/slug which is already used
         * validate through django before saving
         * use good defaults
        """
        key_map = self.config.get('map', {})
        self.keys = {
            "name": key_map.get('name', 'name'),
            "status": key_map.get('status', 'status'),
            "description": key_map.get('description', 'description'),
            "address": key_map.get('address', 'address'),
            "is_published": key_map.get('is_published', 'is_published'),
            "user": key_map.get('user', 'user'),
            "elev": key_map.get('elevation', 'elev'),
            "notes": key_map.get('notes', 'notes'),
        }
        self.default_status = self.config.get('default_status', '')
        
        # retrieve all items
        items = self.data['features']
        
        # init empty lists
        added_nodes = []
        changed_nodes = []
        unmodified_nodes = []
        
        # retrieve a list of all the slugs of this layer
        layer_nodes_slug_list = Node.objects.filter(layer=self.layer).values_list('slug', flat=True)
        # keep a list of all the nodes of other layers
        other_layers_slug_list = Node.objects.exclude(layer=self.layer).values_list('slug', flat=True)
        # init empty list of slug of external nodes that will be needed to perform delete operations
        processed_slug_list = []
        deleted_nodes_count = 0
        
        # loop over every item
        for item in items:
            
            item = self._convert_item(item)
            
            number = 1
            original_name = item['name']
            needed_different_name = False
            
            while True:
                # items might have the same name... so we add a number..
                if item['slug'] in processed_slug_list or item['slug'] in other_layers_slug_list:
                    needed_different_name = True
                    number = number + 1
                    item['name'] = "%s - %d" % (original_name, number)
                    item['slug'] = slugify(item['name'])
                else:
                    if needed_different_name:
                        self.verbose('needed a different name for %s, trying "%s"' % (original_name, item['name']))
                    break
            
            # default values
            added = False
            changed = False
            
            try:
                # edit existing node
                node = Node.objects.get(slug=item['slug'], layer=self.layer)
            except Node.DoesNotExist:
                # add a new node
                node = Node()
                node.layer = self.layer
                added = True
            
            # loop over fields and store data only if necessary
            for field in Node._meta.fields:
                # geometry is a special case, skip
                if field.name == 'geometry':
                    continue
                # skip if field is not present in values
                if field.name not in item.keys():
                    continue
                # if value is different than what we have
                if getattr(node, field.name) != item[field.name]:
                    # set value
                    setattr(node, field.name, item[field.name])
                    # indicates that a DB query is necessary
                    changed = True
            
            if added is True or (
                node.geometry.equals(item['geometry']) is False and
                node.geometry.equals_exact(item['geometry']) is False
                ):
                node.geometry = item['geometry']
                changed = True
            
            node.data = node.data or {}
            
            # store any additional key/value in HStore data field
            for key, value in item['data'].items():
                if node.data[key] != value:
                    node.data[key] = value
                    changed = True
            
            # perform save or update only if necessary
            if added or changed:
                try:
                    node.full_clean()
                    node.save()
                except Exception as e:
                    # TODO: are we sure we want to interrupt the execution?
                    raise Exception('error while processing "%s": %s' % (node.name, e))
            
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
                # store node name to print it later
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