from __future__ import absolute_import

from django.contrib.gis.geos import Point

try:
    from libcnml import CNMLParser
    from libcnml import Status as CNMLStatus
except ImportError:
    raise ImportError('libcnml not installed, install it with "pip install libcnml"')

from nodeshot.core.base.utils import check_dependencies
from nodeshot.core.nodes.models import Node, Status
from nodeshot.networking.net.models import Device, Interface, Ethernet, Wireless, Ip
from nodeshot.networking.links.models import Link
from nodeshot.networking.net.models.choices import INTERFACE_TYPES
from nodeshot.networking.links.models.choices import LINK_TYPES, LINK_STATUS


from .base import GenericGisSynchronizer

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
            'fill_color': '#66ffff',
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        },
        'working': {
            'is_default': False,
            'slug': 'working',
            'description': 'Working nodes',
            'order': 0,
            'name': 'Working',
            "fill_color": "#33ff00",
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        },
        'testing': {
            'is_default': False,
            'slug': 'testing',
            'description': 'Nodes in testing',
            'order': 0,
            'name': 'Testing',
            "fill_color": "#ff9900",
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        },
        'building': {
            'is_default': False,
            'slug': 'building',
            'description': 'Underconstruction nodes',
            'order': 0,
            'name': 'Building',
            "fill_color": "#ffff99",
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        },
        'reserved': {
            'is_default': False,
            'slug': 'reserved',
            'description': 'Reserved nodes',
            'order': 0,
            'name': 'Reserved',
            "fill_color": "#ffffff",
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        },
        'dropped': {
            'is_default': False,
            'slug': 'dropped',
            'description': 'Dropped nodes',
            'order': 0,
            'name': 'Dropped',
            "fill_color": "#ffffff",
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        },
        'inactive': {
            'is_default': False,
            'slug': 'inactive',
            'description': 'Inactive nodes',
            'order': 0,
            'name': 'Inactive',
            "fill_color": "#dddddd",
            'stroke_color': '#000000',
            'stroke_width': 2,
            'text_color': '#000000'
        }
    }

    LINK_TYPE_MAPPING = {
        'wds': 'ethernet',
        'ap/client': 'radio',
        'cable': 'ethernet'
    }

    LINK_STATUS_MAPPING = {
        1: 'planned',
        2: 'active',
        3: 'testing',
        4: 'planned',
        5: 'planned',
        6: 'archived',
        7: 'down',
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
        d = {
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
            "updated": None,
            "data": {
                "cnml_id": str(item.id)
            }
        }

        if item.updated:
            d["updated"] = item.updated.strftime('%Y-%m-%dT%H:%M:%SZ')
        return d

    def save(self):
        self.verbose('PARSING NODES')
        self.save_nodes()
        self.verbose('PARSING DEVICES')
        self.save_devices()
        self.verbose('PARSING INTERFACES')
        self.save_interfaces()
        self.verbose('PARSING LINKS')
        self.save_links()

    def save_nodes(self):
        super(Cnml, self).save()

    def save_devices(self):
        added_devices = []
        deleted_devices = []
        cnml_devices = self.cnml.getDevices()
        current_devices = Device.objects.filter(data__contains=['cnml_id'], node__layer=self.layer)

        total_n = len(cnml_devices)
        for n, cnml_device in enumerate(cnml_devices, 1):
            try:
                device = Device.objects.get(data={'cnml_id':  cnml_device.id})
                added = False
            except Device.DoesNotExist:
                device = Device()
                added = True
            self.verbose('[%d/%d] parsing device "%s" (node: %s)' % (n, total_n, cnml_device.title, cnml_device.parentNode.id))
            node = Node.objects.get(data={'cnml_id': cnml_device.parentNode.id})
            device.name = cnml_device.title,
            device.node = node
            device.type = cnml_device.type
            if cnml_device.firmware:
                try:
                    os, os_version = cnml_device.firmware.split('v')
                except ValueError:
                    os = cnml_device.firmware
                    os_version = ''
            else:
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
        total_n = len(current_devices)
        for n, current_device in enumerate(current_devices, 1):
            self.verbose('[%d/%d] deleting old devices' % (n, total_n))
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

    def save_interfaces(self):
        added_interfaces = []
        deleted_interfaces = []
        cnml_interfaces = self.cnml.getInterfaces()
        current_interfaces = Interface.objects.filter(data__contains=['cnml_id'], device__node__layer=self.layer)

        total_n = len(cnml_interfaces)
        for n, cnml_interface in enumerate(cnml_interfaces, 1):
            self.verbose('[%d/%d] parsing interface "%s" (%s)' % (n, total_n, cnml_interface.id, cnml_interface.ipv4))
            if hasattr(cnml_interface.parentRadio, 'parentDevice'):
                Model = Wireless
            else:
                Model = Ethernet
            try:
                interface = Model.objects.get(data={'cnml_id':  cnml_interface.id})
                added = False
            except Model.DoesNotExist:
                interface = Model()
                added = True
            if Model is Wireless:
                parent = cnml_interface.parentRadio.parentDevice.id
            else:
                parent = cnml_interface.parentRadio.id
                interface.duplex = 'full'
                interface.standard = 'fast'
            device = Device.objects.get(data={'cnml_id': parent})
            interface.type = INTERFACE_TYPES.get(Model.__name__.lower())
            interface.device = device
            interface.data['cnml_id'] = cnml_interface.id
            interface.full_clean()
            interface.save()

            if cnml_interface.ipv4:
                # in CNML interfaces have always only 1 IP
                try:
                    ip = Ip.objects.get(address=cnml_interface.ipv4)
                except Ip.DoesNotExist:
                    ip = Ip()
                ip.interface = interface
                ip.address = cnml_interface.ipv4
                ip.netmask = cnml_interface.mask
                ip.full_clean()
                ip.save()

            if added:
                added_interfaces.append(interface)

        # delete interfaces that are not in CNML anymore
        total_n = len(current_interfaces)
        for n, current_interface in enumerate(current_interfaces, 1):
            self.verbose('[%d/%d] deleting old interfaces' % (n, total_n))
            try:
                self.cnml.getInterface(int(current_interface.data['cnml_id']))
            except KeyError:
                deleted_interfaces.append(current_interface)
                current_interface.delete()

        self.message += """
            %s interfaces added
            %s interfaces deleted
        """ % (
            len(added_interfaces),
            len(deleted_interfaces)
        )

    def save_links(self):
        added_links = []
        deleted_links = []
        cnml_links = self.cnml.getLinks()
        current_links = Link.objects.filter(data__contains=['cnml_id'], layer=self.layer)
        # keep a list of link cnml_id
        # TODO: hstore seems to not work properly, something is wrong
        cnml_id_list = []
        cnml_id_mapping = {}
        for current_link in current_links:
            cnml_id_list.append(current_link.data['cnml_id'])
            cnml_id_mapping[current_link.data['cnml_id']] = current_link.id

        total_n = len(cnml_links)
        for n, cnml_link in enumerate(cnml_links, 1):
            if str(cnml_link.id) in cnml_id_list:
                try:
                    link_id = cnml_id_mapping[str(cnml_link.id)]
                # probably a link between a node of another zone
                except KeyError:
                    continue
                link = Link.objects.get(id=link_id)
                added = False
            else:
                link = Link()
                added = True
            # link between a node which is not of this CNML zone
            if isinstance(cnml_link.nodeA, int) or isinstance(cnml_link.nodeB, int):
                continue
            node_a = Node.objects.get(data={'cnml_id': cnml_link.nodeA.id})
            node_b = Node.objects.get(data={'cnml_id': cnml_link.nodeB.id})
            link.node_a = node_a
            link.node_b = node_b
            link.type = LINK_TYPES.get(self.LINK_TYPE_MAPPING[cnml_link.type])
            link.status = LINK_STATUS.get(self.LINK_STATUS_MAPPING[cnml_link.status])
            self.verbose('[%d/%d] parsing link "%s" (%s<-->%s)' % (n, total_n, cnml_link.id, node_a, node_b))
            # set interface_a and interface_b only if not planned
            # because there might be inconsistencies in the CNML from guifi.net
            if link.get_status_display() != 'planned':
                if cnml_link.interfaceA:
                    interface_a = Interface.objects.get(data={'cnml_id': cnml_link.interfaceA.id})
                    link.interface_a = interface_a
                if cnml_link.interfaceB:
                    interface_b = Interface.objects.get(data={'cnml_id': cnml_link.interfaceB.id})
                    link.interface_b = interface_b
            else:
                link.interface_a = None
                link.interface_b = None
            link.data['cnml_id'] = cnml_link.id
            try:
                link.full_clean()
            except Exception as e:
                print(e)
                continue
            link.save()

            if added:
                added_links.append(link)

        # delete links that are not in CNML anymore
        total_n = len(current_links)
        for n, current_link in enumerate(current_links, 1):
            self.verbose('[%d/%d] deleting old links' % (n, total_n))
            try:
                self.cnml.getLink(int(current_link.data['cnml_id']))
            except KeyError:
                deleted_links.append(current_link)
                current_link.delete()

        self.message += """
            %s links added
            %s links deleted
        """ % (
            len(added_links),
            len(deleted_links)
        )
