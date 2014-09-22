from __future__ import absolute_import

from nodeshot.interoperability.synchronizers import GeoJson
from .citysdk_mobility import CitySdkMobilityMixin


class GeoJsonCitySdkMobility(CitySdkMobilityMixin, GeoJson):
    """ Import GeoJson and sync CitySDK """

    REQUIRED_CONFIG_KEYS = [
        'url',
        'map',
        'citysdk_url',
        'citysdk_layer',
        'citysdk_username',
        'citysdk_password'
    ]
