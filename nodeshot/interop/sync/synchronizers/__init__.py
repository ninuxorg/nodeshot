from __future__ import absolute_import
from django.conf import settings

from .nodeshot import Nodeshot
from .geojson import GeoJson
from .georss import GeoRss
from .openwisp import OpenWisp

__all__ = [
    'Nodeshot',
    'GeoJson',
    'GeoRss',
    'OpenWisp'
]

if 'nodeshot.networking.links' in settings.INSTALLED_APPS:
    from .cnml import Cnml  # noqa
    __all__.append('Cnml')
