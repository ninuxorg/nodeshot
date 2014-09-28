from __future__ import absolute_import

from .provinciawifi import ProvinciaWifi
from .citysdk_tourism import CitySdkTourismMixin


class ProvinciaWifiCitySdkTourism(CitySdkTourismMixin, ProvinciaWifi):
    """
    ProvinciaWifiCitySdkTourism synchronizer
    Imports data from Provincia WIFI in the local DB and it also sends it
    to CitySDK tourism API
    """
    SCHEMA = CitySdkTourismMixin.SCHEMA + ProvinciaWifi.SCHEMA
