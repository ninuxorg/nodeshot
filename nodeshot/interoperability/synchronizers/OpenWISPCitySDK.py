from .OpenWISP import OpenWISP
from .CitySDKMixin import CitySDKMixin


class OpenWISPCitySDK(CitySDKMixin, OpenWISP):
    """
    OpenWISPCitySDK interoperability class
    Imports data from OpenWISP GeoRSS and then exports the data to the CitySDK database
    """
    pass