from .ProvinciaWifi import ProvinciaWifi
from .CitySdkTourism import CitySdkTourismMixin


class ProvinciaWifiCitySdkTourism(CitySdkTourismMixin, ProvinciaWifi):
    """
    ProvinciaWifiCitySdkTourism synchronizer
    Imports data from Provincia WIFI in the local DB and it also sends it
    to CitySDK tourism API
    """
    pass
