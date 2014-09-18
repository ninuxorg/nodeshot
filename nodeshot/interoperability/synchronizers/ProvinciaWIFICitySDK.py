from .ProvinciaWIFI import ProvinciaWIFI
from .CitySdkTourism import CitySdkTourismMixin


class ProvinciaWIFICitySDK(CitySdkTourismMixin, ProvinciaWIFI):
    """
    ProvinciaWIFICitySDK interoperability class
    Imports data from Provincia WIFI Open Data and then exports the data to the CitySDK database
    """
    pass
