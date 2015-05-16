from django.conf import settings

DEFAULT_PARSERS = [
    ('netdiff.OlsrParser', 'OLSR (jsoninfo)'),
    ('netdiff.BatmanParser', 'batman-advanced (alfred-vis)'),
    ('netdiff.BmxParser', 'BMX6 (q6m)'),
    ('netdiff.NetJsonParser', 'NetJSON NetworkGraph'),
    ('netdiff.CnmlParser', 'CNML'),
]

PARSERS = DEFAULT_PARSERS + getattr(settings, 'NODESHOT_NETDIFF_PARSERS', [])
