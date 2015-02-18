from __future__ import absolute_import

import requests
from xml.dom import minidom
from dateutil import parser as DateParser

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.utils import pause_disconnectable_signals, resume_disconnectable_signals
from nodeshot.core.nodes.models import Node, Status


__all__ = [
    # classes
    'BaseSynchronizer',
    'XmlSynchronizer',
    'GenericGisSynchronizer',
    # mixins
    'HttpRetrieverMixin',
    'XMLParserMixin',
]


class BaseSynchronizer(object):
    """
    Base Synchronizer
    Provides methods for:
        * config validation
        * django validation
        * executing actions before or after specific events
        * retrieve data
        * extract data from imported source
        * save data into DB
        * log messages with different levels of verbosity
    """
    SCHEMA = None

    def __init__(self, layer, *args, **kwargs):
        """
        :layer models.Model: instance of Layer we want to convert
        """
        self.layer = layer
        self.verbosity = kwargs.get('verbosity', 1)
        self.load_config()

    def load_config(self, config=None):
        self.config = config or self.layer.external.config
        self.verify_ssl = self.config.get('verify_ssl', True)
        # ensure correct boolean
        self.verify_ssl = self.verify_ssl is True or self.verify_ssl == 'True'

    def clean(self):
        """ complex ad hoc validation here, will be executed before the external layer is saved """
        pass

    def after_external_layer_saved(self, *args, **kwargs):
        """ anything that should be executed after the external layer is saved goes here """
        pass

    def before_start(self, *args, **kwargs):
        """ anything that should be executed before the import starts goes here """
        pass

    def after_complete(self, *args, **kwargs):
        """ anything that should be executed after the import is complete goes here """
        pass

    def process(self):
        """
        This is the method that does everything automatically (at least attempts to).

        Steps:
            0. Call "before_start" method (which might be implemented by children classes)
            1. Retrieve data from external source
            2. Parse the data
            3. Save the data locally
            4. Call "after_complete" method (which might be implemented by children classes)
        """
        self.before_start()
        self.retrieve_data()
        self.parse()

        # TRICK: disable new_nodes_allowed_for_layer validation
        try:
            Node._additional_validation.remove('new_nodes_allowed_for_layer')
        except ValueError as e:
            print "WARNING! got exception: %s" % e
        # avoid sending zillions of notifications
        pause_disconnectable_signals()

        self.save()

        # Re-enable new_nodes_allowed_for_layer validation
        try:
            Node._additional_validation.insert(0, 'new_nodes_allowed_for_layer')
        except ValueError as e:
            print "WARNING! got exception: %s" % e
        # reconnect signals
        resume_disconnectable_signals()

        self.after_complete()

        # return message as a list because more than one messages might be returned
        return [self.message]

    def retrieve_data(self):
        """ retrieve data """
        raise NotImplementedError("BaseSynchronizer child class does not implement a retrieve_data method")

    def parse(self):
        """ parse data """
        raise NotImplementedError("BaseSynchronizer child class does not implement a parse method")

    def save(self):
        """ save data into DB """
        raise NotImplementedError("BaseSynchronizer child class does not implement a save method")

    def verbose(self, message):
        if self.verbosity >= 2:
            print(message)


class HttpRetrieverMixin(object):
    """ Retrieve external data through HTTP """

    def retrieve_data(self):
        """ retrieve data from an HTTP URL """
        # shortcuts for readability
        url = self.config.get('url')

        # do HTTP request and store content
        self.data = requests.get(url, verify=self.verify_ssl).content


class XMLParserMixin(object):
    """ XML Parsing utility methods """

    def parse(self):
        """ parse data """
        self.parsed_data = minidom.parseString(self.data)

    @staticmethod
    def get_text(item, tag, default=False):
        """ returns text content of an xml tag """
        try:
            xmlnode = item.getElementsByTagName(tag)[0].firstChild
        except IndexError as e:
            if default is not False:
                return default
            else:
                raise IndexError(e)

        if xmlnode is not None:
            return unicode(xmlnode.nodeValue)
        # empty tag
        else:
            return ''


class GenericGisSynchronizer(HttpRetrieverMixin, BaseSynchronizer):
    """
    Base Synchronizer for GIS formats like geojson, georss, kml, ecc

    It does not supports all the formats, rather it provides an easy way to add support for each format.

    You must implement a "parse_item" method to support different formats.
    """
    SCHEMA = [
        {
            'name': 'url',
            'class': 'CharField',
            'kwargs': {
                'max_length': 128,
                'help_text': _('URL containing geographical data')
            }
        },
        {
            'name': 'verify_ssl',
            'class': 'BooleanField',
            'kwargs': {
                'default': True,
                'help_text': _('Wether the SSL certificates of the external services used should be verified or not')
            }
        },
        {
            'name': 'default_status',
            'class': 'CharField',
            'kwargs': {
                'blank': True,
                'max_length': 255,
                'help_text': _('Status for imported nodes, leave blank to use the default one')
            }
        },
        {
            'name': 'field_name',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'name',
                'verbose_name': _('name field'),
                'help_text': _('corresponding name field on external source')
            }
        },
        {
            'name': 'field_status',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'status',
                'verbose_name': _('status field'),
                'help_text': _('corresponding status field on external source')
            }
        },
        {
            'name': 'field_description',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'description',
                'verbose_name': _('description field'),
                'help_text': _('corresponding description field on external source')
            }
        },
        {
            'name': 'field_address',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'address',
                'verbose_name': _('address field'),
                'help_text': _('corresponding address field on external source')
            }
        },
        {
            'name': 'field_is_published',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'is_published',
                'verbose_name': _('is_published field'),
                'help_text': _('corresponding is_published field on external source')
            }
        },
        {
            'name': 'field_user',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'user',
                'verbose_name': _('user field'),
                'help_text': _('corresponding user field on external source')
            }
        },
        {
            'name': 'field_elev',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'elev',
                'verbose_name': _('elev field'),
                'help_text': _('corresponding elev field on external source')
            }
        },
        {
            'name': 'field_notes',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'notes',
                'verbose_name': _('notes field'),
                'help_text': _('corresponding notes field on external source')
            }
        },
        {
            'name': 'field_added',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'added',
                'verbose_name': _('added field'),
                'help_text': _('corresponding added field on external source')
            }
        },
        {
            'name': 'field_updated',
            'class': 'CharField',
            'kwargs': {
                'max_length': 64,
                'default': 'updated',
                'verbose_name': _('updated field'),
                'help_text': _('corresponding updated field on external source')
            }
        }
    ]

    def __init__(self, layer, *args, **kwargs):
        super(GenericGisSynchronizer, self).__init__(layer, *args, **kwargs)
        # init empty dict
        self.field_mapping = {}
        # include all keys which start with 'field_'
        for key, value in layer.external.config.items():
            if key.startswith('field_'):
                # replace 'field_' prefix
                key = key.replace('field_', '')
                self.field_mapping[key] = value

    def parse_item(self, item):
        """
        override this method according to the format you want to support.

        Should return a dictionary with the following structure:

        result = {
            "name": "string required",
            "status": "string or None",
            "address": "string or empty string",
            "is_published": "boolean",
            "user": "username or None",
            "geometry": "GEOSGeometry object",
            "elev": "float or none",
            "description": "string or empty string",
            "notes": "string or empty string",
            "added", "string date representation",
            "updated", "string date representation",
        }
        """
        raise NotImplementedError("Not Implemented")

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

        # convert dates to python datetime
        try:
            item['added'] = DateParser.parse(item['added'])
        except Exception as e:
            print "Exception while parsing 'added' date: %s" % e
        try:
            item['updated'] = DateParser.parse(item['updated'])
        except Exception as e:
            print "Exception while parsing 'updated' date: %s" % e

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
            "added": item['added'],
            "updated": item['updated'],
            "data": {}
        }

        # ensure all additional data items are strings
        for key, value in item['data'].items():
            result["data"][key] = value

        return result

    def key_mapping(self):
        key_map = self.field_mapping
        self.keys = {
            "name": key_map.get('name', 'name'),
            "status": key_map.get('status', 'status'),
            "description": key_map.get('description', 'description'),
            "address": key_map.get('address', 'address'),
            "is_published": key_map.get('is_published', 'is_published'),
            "user": key_map.get('user', 'user'),
            "elev": key_map.get('elev', 'elev'),
            "notes": key_map.get('notes', 'notes'),
            "added": key_map.get('added', 'added'),
            "updated": key_map.get('updated', 'updated'),
        }
        self.default_status = self.config.get('default_status', '')

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
        self.key_mapping()
        # retrieve all items
        items = self.parsed_data

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
                # shortcut for value
                value = item[field.name]
                # if value is different than what we have
                if getattr(node, field.name) != value and value is not None:
                    # set value
                    setattr(node, field.name, value)
                    # indicates that a DB query is necessary
                    changed = True

            if added is True or (node.geometry.equals(item['geometry']) is False\
                                 and node.geometry.equals_exact(item['geometry']) is False):
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
                    if node.added is not None and node.updated is not None:
                        node.save(auto_update=False)
                    else:
                        node.save()
                except Exception as e:
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
            if local_node not in processed_slug_list:
                # retrieve from DB and delete
                node = Node.objects.get(slug=local_node)
                # store node name to print it later
                node_name = node.name
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


class XmlSynchronizer(HttpRetrieverMixin, XMLParserMixin, BaseSynchronizer):
    """ XML HTTP syncrhonizer """
