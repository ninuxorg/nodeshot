from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies='nodeshot.core.nodes',
    module='nodeshot.networking.net'
)


from routing_protocol import RoutingProtocol
from device import Device
from interface import Interface
from ip import Ip

from interfaces.ethernet import Ethernet
from interfaces.wireless import Wireless
from interfaces.bridge import Bridge
from interfaces.tunnel import Tunnel
from interfaces.vlan import Vlan
from interfaces.vap import Vap


__all__ = [
    'RoutingProtocol',
    'Device',
    'Interface',
    'Ip',
    'Ethernet',
    'Wireless',
    'Bridge',
    'Tunnel',
    'Vlan',
    'Vap'
]


# ------ Add relationship to ExtensibleNodeSerializer ------ #

from nodeshot.core.nodes.base import ExtensibleNodeSerializer

ExtensibleNodeSerializer.add_relationship(**{
    'name': 'devices',
    'view_name': 'api_node_devices',
    'lookup_field': 'slug'
})