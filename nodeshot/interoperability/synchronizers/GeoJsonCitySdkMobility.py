from .GeoJson import GeoJson
from .CitySdkMobility import CitySdkMobilityMixin


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