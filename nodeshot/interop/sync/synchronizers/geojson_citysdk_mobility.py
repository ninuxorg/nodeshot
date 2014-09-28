from __future__ import absolute_import

from nodeshot.interop.sync.synchronizers import GeoJson
from .citysdk_mobility import CitySdkMobilityMixin


class GeoJsonCitySdkMobility(CitySdkMobilityMixin, GeoJson):
    """ Import GeoJson and sync CitySDK """
    SCHEMA = CitySdkMobilityMixin.SCHEMA + GeoJson.SCHEMA
