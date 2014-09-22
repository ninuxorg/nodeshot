from .ProvinciaWifi import ProvinciaWifi
from .CitySdkMobility import CitySdkMobilityMixin


class ProvinciaWifiCitySdkMobility(CitySdkMobilityMixin, ProvinciaWifi):
    """
    ProvinciaWIFICitySDK interoperability class
    Imports data from Provincia WIFI Open Data and then exports the data to the CitySDK Mobility API database
    """

    REQUIRED_CONFIG_KEYS = [
        'url',
        'citysdk_url',
        'citysdk_layer',
        'citysdk_username',
        'citysdk_password'
    ]
