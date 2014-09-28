from __future__ import absolute_import

from .provinciawifi import ProvinciaWifi
from .citysdk_mobility import CitySdkMobilityMixin


class ProvinciaWifiCitySdkMobility(CitySdkMobilityMixin, ProvinciaWifi):
    """
    ProvinciaWifiCitySdkMobility synchronizer
    Imports data from Provincia WIFI in the local DB and it also sends it
    to CitySDK mobility API
    """
    SCHEMA = CitySdkMobilityMixin.SCHEMA + ProvinciaWifi.SCHEMA
