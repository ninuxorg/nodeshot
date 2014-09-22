from django.conf import settings


DEFAULT_SYNCHRONIZERS = [
    ('nodeshot.interoperability.synchronizers.Nodeshot', 'Nodeshot'),
    ('nodeshot.interoperability.synchronizers.GeoJson', 'GeoJSON'),
    ('nodeshot.interoperability.synchronizers.GeoRss', 'GeoRSS'),
    ('nodeshot.interoperability.synchronizers.OpenWisp', 'OpenWisp'),
    ('nodeshot.interoperability.synchronizers.OpenWispCitySdkTourism', 'OpenWispCitySdkTourism'),
    ('nodeshot.interoperability.synchronizers.ProvinciaWifi', 'Provincia WiFi'),
    ('nodeshot.interoperability.synchronizers.ProvinciaWifiCitySdkTourism', 'ProvinciaWifiCitySdkTourism'),
    ('nodeshot.interoperability.synchronizers.ProvinciaWifiCitySdkMobility', 'Synchronize Provincia Wifi with CitySDK Mobility'),
    ('nodeshot.interoperability.synchronizers.CitySdkMobility', 'CitySDK Mobility (event driven)'),
    ('nodeshot.interoperability.synchronizers.GeoJsonCitySdkMobility', 'Import GeoJSON into CitySDK Mobility API'),
    ('nodeshot.interoperability.synchronizers.GeoJsonCitySdkTourism', 'Import GeoJSON into CitySDK Tourism API'),
    ('nodeshot.interoperability.synchronizers.OpenLabor', 'OpenLabor'),
]

SYNCHRONIZERS = DEFAULT_SYNCHRONIZERS + getattr(settings, 'NODESHOT_SYNCHRONIZERS', [])

CITYSDK_TOURISM_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_TOURISM_TEST_CONFIG', False)
CITYSDK_MOBILITY_TEST_CONFIG = getattr(settings, 'NODESHOT_CITYSDK_MOBILITY_TEST_CONFIG', False)
