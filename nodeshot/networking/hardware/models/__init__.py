# this app is dependant on "net"
from django.conf import settings
if 'nodeshot.networking.net' not in settings.INSTALLED_APPS:
    from nodeshot.core.base.exceptions import DependencyError
    raise DependencyError('nodeshot.networking.hardware depends on nodeshot.networking.net, which should be in settings.INSTALLED_APPS')

from base import ImageMixin
from manufacturer import Manufacturer
from mac_prefix import MacPrefix
from device_model import DeviceModel
from antenna_model import AntennaModel
from radiation_pattern import RadiationPattern
from antenna import Antenna
from device_to_model_rel import DeviceToModelRel


__all__ = [
    'ImageMixin',
    'Manufacturer',
    'MacPrefix',
    'DeviceModel',
    'AntennaModel',
    'RadiationPattern',
    'Antenna',
    'DeviceToModelRel'
]
