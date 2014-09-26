from django.conf import settings


DEFAULT_SYNCHRONIZERS = [
    ('nodeshot.interop.sync.synchronizers.Nodeshot', 'Nodeshot (RESTful translator)'),
    ('nodeshot.interop.sync.synchronizers.GeoJson', 'GeoJSON (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.GeoRss', 'GeoRSS (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.OpenWisp', 'OpenWisp (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.OpenWispCitySdkTourism', 'OpenWISP CitySDK Tourism (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.ProvinciaWifi', 'Provincia WiFi (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.ProvinciaWifiCitySdkTourism', 'Provincia WiFi CitySDK Tourism (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.ProvinciaWifiCitySdkMobility', 'Provincia WiFi CitySDK Mobility (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.CitySdkMobility', 'CitySDK Mobility (event driven)'),
    ('nodeshot.interop.sync.synchronizers.CitySdkTourism', 'CitySDK Tourism (event driven)'),
    ('nodeshot.interop.sync.synchronizers.GeoJsonCitySdkMobility', 'GeoJSON CitySDK Mobility (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.GeoJsonCitySdkTourism', 'GeoJSON CitySDK Tourism (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.OpenLabor', 'OpenLabor (RESTful translator + event driven)'),
    ('nodeshot.interop.sync.synchronizers.ProvinceRomeTraffic', 'Province of Rome Traffic')
]

SYNCHRONIZERS = DEFAULT_SYNCHRONIZERS + getattr(settings, 'NODESHOT_SYNCHRONIZERS', [])

CITYSDK_TOURISM_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_TOURISM_TEST_CONFIG', False)
CITYSDK_MOBILITY_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_MOBILITY_TEST_CONFIG', False)
