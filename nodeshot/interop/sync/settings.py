from django.conf import settings


DEFAULT_SYNCHRONIZERS = [
    ('nodeshot.interop.sync.synchronizers.Nodeshot', 'Nodeshot (RESTful translator)'),
    ('nodeshot.interop.sync.synchronizers.GeoJson', 'GeoJSON (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.GeoRss', 'GeoRSS (periodic sync)'),
    ('nodeshot.interop.sync.synchronizers.OpenWisp', 'OpenWisp (periodic sync)')
]

SYNCHRONIZERS = DEFAULT_SYNCHRONIZERS + getattr(settings, 'NODESHOT_SYNCHRONIZERS', [])
