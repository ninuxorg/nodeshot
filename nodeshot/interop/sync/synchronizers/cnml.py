from __future__ import absolute_import

import pytz

from django.contrib.gis.geos import Point

#from django.utils.translation import ugettext_lazy as _

try:
    from libcnml import CNMLParser
    from libcnml import Status as CNMLStatus
except ImportError:
    raise ImportError('libcnml not installed, install it with "pip install libcnml"')

from nodeshot.core.base.utils import check_dependencies
from nodeshot.core.nodes.models import Node, Status
from nodeshot.networking.net.models import Device

from .base import BaseSynchronizer, GenericGisSynchronizer

check_dependencies(
    dependencies=[
        'nodeshot.networking.net',
        'nodeshot.networking.links',
    ],
    module='nodeshot.interop.sync.synchronizers.cnml'
)


class Cnml(GenericGisSynchronizer):
    """ CNML synchronizer """
    SCHEMA = GenericGisSynchronizer.SCHEMA[0:2]

    STATUS_MAPPING = {
        'planned': {
            'is_default': True,
            'slug': 'planned',
            'description': 'Planned node',
            'order': 0,
            'name': 'Planned',
            'fill_color': '#ff8000',
            'stroke_color': '#ec7600',
            'stroke_width': 2,
            'text_color': '#ffffff'
        },
        'working': {
            'is_default': False,
            'slug': 'working',
            'description': 'Working nodes',
            'order': 0,
            'name': 'Working',
            "fill_color": "#008000",
            "stroke_color": "#005e00",
            'stroke_width': 2,
            'text_color': '#ffffff'
        },
        'testing': {
            'is_default': False,
            'slug': 'testing',
            'description': 'Nodes in testing',
            'order': 0,
            'name': 'Testing',
            "fill_color": "#007000",
            "stroke_color": "#007e00",
            'stroke_width': 2,
            'text_color': '#ffffff'
        },
        'building': {
            'is_default': False,
            'slug': 'building',
            'description': 'Underconstruction nodes',
            'order': 0,
            'name': 'Building',
            "fill_color": "#003000",
            "stroke_color": "#003000",
            'stroke_width': 2,
            'text_color': '#ffffff'
        },
        'reserved': {
            'is_default': False,
            'slug': 'reserved',
            'description': 'Reserved nodes',
            'order': 0,
            'name': 'Reserved',
            "fill_color": "#002000",
            "stroke_color": "#002000",
            'stroke_width': 2,
            'text_color': '#ffffff'
        },
        'dropped': {
            'is_default': False,
            'slug': 'dropped',
            'description': 'Dropped nodes',
            'order': 0,
            'name': 'Dropped',
            "fill_color": "#002000",
            "stroke_color": "#002000",
            'stroke_width': 2,
            'text_color': '#ffffff'
        },
        'inactive': {
            'is_default': False,
            'slug': 'inactive',
            'description': 'Inactive nodes',
            'order': 0,
            'name': 'Inactive',
            "fill_color": "#001000",
            "stroke_color": "#001000",
            'stroke_width': 2,
            'text_color': '#ffffff'
        }
    }

    def parse(self):
        """ parse data """
        url = self.config.get('url')
        self.cnml = CNMLParser(url)
        self.parsed_data = self.cnml.getNodes()

    def before_start(self):
        self._ensure_status()

    def _ensure_status(self):
        for key, status_data in self.STATUS_MAPPING.items():
            if Status.objects.filter(slug__exact=key).count() < 1:
                new_status = Status(**status_data)
                new_status.full_clean()
                new_status.save()

    def retrieve_data(self):
        """ not needed """
        pass

    def key_mapping(self):
        """ not needed """
        pass

    def parse_item(self, item):
        return {
            "name": item.title,
            "status": CNMLStatus.statusToStr(item.status),
            "address": "",
            "is_published": True,
            "user": None,
            "geometry": Point(item.longitude, item.latitude),
            "elev": item.antenna_elevation,
            "description": '<a href="https://guifi.net/node/{0}" target="_blank">guifi.net/node/{0}</a>'.format(item.id),
            "notes": "",
            "added": item.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "updated": item.updated.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "data": {
                "cnml_id": str(item.id)
            }
        }

    def save(self):
        self.save_nodes()
        self.save_devices()

    def save_nodes(self):
        super(Cnml, self).save()

    def save_devices(self):
        added_devices = []
        deleted_devices = []
        cnml_devices = self.cnml.getDevices()
        current_devices = Device.objects.filter(data__contains=['cnml_id'])

        for cnml_device in cnml_devices:
            try:
                device = Device.objects.get(data={'cnml_id':  cnml_device.id })
                added = False
            except Device.DoesNotExist:
                device = Device()
                added = True
            node = Node.objects.get(data={'cnml_id': cnml_device.parentNode.id})
            device.name = str(cnml_device.title),
            device.node = node
            device.type = cnml_device.type
            try:
                os, os_version = cnml_device.firmware.split('v')
            except ValueError:
                os = cnml_device.firmware
                os_version = ''
            device.os = os
            device.os_version = os_version
            device.data['cnml_id'] = cnml_device.id
            device.full_clean()
            device.save()

            if added:
                added_devices.append(device)

        # delete devices that are not in CNML anymore
        for current_device in current_devices:
            try:
                self.cnml.getDevice(int(current_device.data['cnml_id']))
            except KeyError:
                deleted_devices.append(current_device)
                current_device.delete()

        self.message += """
            %s devices added
            %s devices deleted
        """ % (
            len(added_devices),
            len(deleted_devices)
        )
