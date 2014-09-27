from __future__ import absolute_import

import requests
import simplejson as json
from datetime import date, datetime, timedelta

from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError

from nodeshot.core.nodes.models import Node, Status
from nodeshot.interop.sync.synchronizers.base import BaseSynchronizer


class ProvinceRomeTraffic(BaseSynchronizer):
    """ Province of Rome Traffic synchronizer class """
    SCHEMA = [
        {
            'name': 'streets_url',
            'class': 'URLField'
        },
        {
            'name': 'measurements_url',
            'class': 'URLField'
        },
        {
            'name': 'check_streets_every_n_days',
            'class': 'IntegerField',
            'kwargs': { 'default': 2 }
        }
    ]

    def retrieve_data(self):
        """ retrieve data """
        # shortcuts for readability
        streets_url = self.config.get('streets_url')
        check_streets_every_n_days = int(self.config.get('check_streets_every_n_days', 2))
        last_time_streets_checked = self.config.get('last_time_streets_checked', None)
        measurements_url = self.config.get('measurements_url')

        # do HTTP request and store content
        self.measurements = requests.get(measurements_url, verify=self.verify_ssl).content

        try:
            last_time_streets_checked = datetime.strptime(last_time_streets_checked, '%Y-%m-%d').date()
        except TypeError:
            pass

        # if last time checked more than days specified
        if last_time_streets_checked is None or last_time_streets_checked < date.today() - timedelta(days=check_streets_every_n_days):
            # get huge streets file
            self.streets = requests.get(streets_url, verify=self.verify_ssl).content
        else:
            self.streets = False

    def parse(self):
        """ parse data """
        self.measurements = json.loads(self.measurements)["features"]
        if self.streets:
            self.streets = json.loads(self.streets)["features"]

    def save(self):
        """ synchronize DB """
        self.process_streets()
        self.process_measurements()

    def process_measurements(self):
        items = self.measurements
        if len(items) < 1:
            self.message += """
            No measurements found.
            """
        else:
            saved_measurements = 0
            for item in items:
                try:
                    node = Node.objects.get(pk=int(item['id']))
                except Node.DoesNotExist:
                    print "Could not retrieve node #%s" % item['id']
                    continue
                try:
                    node.data['last_measurement'] = item['properties']['TIMESTAMP']
                    node.data['velocity'] = item['properties']['VELOCITY']
                    node.save()
                    self.verbose('Updated measurement for node %s' % node.id)
                    saved_measurements += 1
                except KeyError:
                    pass
            self.message += """
            Updated measurements of %d street segments out of %d
            """ % (saved_measurements, len(items))

    def process_streets(self):
        if not self.streets:
            self.message = """
            Street data not processed.
            """
            return False
        # retrieve all items
        items = self.streets

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
            pk = item['id']
            name = item['properties'].get('LOCATION', '')[0:70]
            address = name
            slug = slugify(name)

            number = 1
            original_name = name
            needed_different_name = False

            while True:
                # items might have the same name... so we add a number..
                # check in DB too
                if slug in external_nodes_slug or Node.objects.filter(slug__exact=slug).exclude(pk=pk).count() > 0:
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
                node = Node.objects.get(pk=pk)
            except Node.DoesNotExist:
                # add a new node
                node = Node()
                node.id = pk
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
            external_nodes_slug.append(node.slug)

        # delete old nodes
        for local_node in local_nodes_slug:
            # if local node not found in external nodes
            if local_node not in external_nodes_slug:
                node_name = node.name
                # retrieve from DB and delete
                node = Node.objects.get(slug=local_node)
                node.delete()
                # then increment count that will be included in message
                deleted_nodes_count = deleted_nodes_count + 1
                self.verbose('node "%s" deleted' % node_name)

        self.config['last_time_streets_checked'] = str(date.today())
        self.layer.external.config = self.config
        self.layer.external.save()

        # message that will be returned
        self.message = """
            %s streets added
            %s streets changed
            %s streets deleted
            %s streets unmodified
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
