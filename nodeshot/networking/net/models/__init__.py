# this app is dependant on "node"
from django.conf import settings
if 'nodeshot.core.nodes' not in settings.INSTALLED_APPS:
    from nodeshot.core.base.exceptions import DependencyError
    raise DependencyError('nodeshot.networking.net depends on nodeshot.core.nodes, which should be in settings.INSTALLED_APPS')

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