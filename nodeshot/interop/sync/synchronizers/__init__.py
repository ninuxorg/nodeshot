from __future__ import absolute_import

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

# --- citysdk (will be moved in a separate package soon) --- #

from .citysdk_mobility import CitySdkMobility
from .citysdk_tourism import CitySdkTourism
from .geojson_citysdk_mobility import GeoJsonCitySdkMobility
from .geojson_citysdk_tourism import GeoJsonCitySdkTourism
from .openwisp_citysdk_tourism import OpenWispCitySdkTourism
from .provinciawifi import ProvinciaWifi
from .provinciawifi_citysdk_mobility import ProvinciaWifiCitySdkMobility
from .provinciawifi_citysdk_tourism import ProvinciaWifiCitySdkTourism
from .provincerometraffic import ProvinceRomeTraffic
from .openlabor import OpenLabor

__all__ = __all__ + [
    'CitySdkMobility',
    'CitySdkTourism',
    'GeoJsonCitySdkMobility',
    'GeoJsonCitySdkTourism',
    'OpenWispCitySdkTourism',
    'ProvinciaWifi',
    'ProvinciaWifiCitySdkMobility',
    'ProvinciaWifiCitySdkTourism',
    'ProvinceRomeTraffic',
    'OpenLabor',
]
