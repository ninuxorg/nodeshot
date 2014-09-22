from django.conf import settings


DEFAULT_SYNCHRONIZERS = [
    ('nodeshot.interoperability.synchronizers.Nodeshot', 'Nodeshot (RESTful translator)'),
    ('nodeshot.interoperability.synchronizers.GeoJson', 'GeoJSON (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.GeoRss', 'GeoRSS (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.OpenWisp', 'OpenWisp (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.OpenWispCitySdkTourism', 'OpenWISP CitySDK Tourism (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.ProvinciaWifi', 'Provincia WiFi (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.ProvinciaWifiCitySdkTourism', 'Provincia WiFi CitySDK Tourism (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.ProvinciaWifiCitySdkMobility', 'Provincia WiFi CitySDK Mobility (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.CitySdkMobility', 'CitySDK Mobility (event driven)'),
    ('nodeshot.interoperability.synchronizers.CitySdkTourism', 'CitySDK Tourism (event driven)'),
    ('nodeshot.interoperability.synchronizers.GeoJsonCitySdkMobility', 'GeoJSON CitySDK Mobility (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.GeoJsonCitySdkTourism', 'GeoJSON CitySDK Tourism (periodic sync)'),
    ('nodeshot.interoperability.synchronizers.OpenLabor', 'OpenLabor (RESTful translator + event driven)'),
]

SYNCHRONIZERS = DEFAULT_SYNCHRONIZERS + getattr(settings, 'NODESHOT_SYNCHRONIZERS', [])

CITYSDK_TOURISM_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_TOURISM_TEST_CONFIG', False)
CITYSDK_MOBILITY_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_MOBILITY_TEST_CONFIG', False)
