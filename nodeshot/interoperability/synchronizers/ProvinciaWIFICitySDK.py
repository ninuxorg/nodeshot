from .ProvinciaWIFI import ProvinciaWIFI
from .CitySDKMixin import CitySDKMixin


class ProvinciaWIFICitySDK(CitySDKMixin, ProvinciaWIFI):
    """
    ProvinciaWIFICitySDK interoperability class
    Imports data from Provincia WIFI Open Data and then exports the data to the CitySDK database
    """
    pass