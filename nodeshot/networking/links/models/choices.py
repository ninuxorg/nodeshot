
LINK_STATUS = {
    'archived': -3,
    'disconnected': -2,
    'down': -1,
    'planned': 0,
    'testing': 1,
    'active': 2
}

LINK_TYPES = {
    'radio': 1,
    'ethernet': 2,
    'fiber': 3,
    'other_wired': 4,
    'virtual': 5
}

# TODO: pheraphs this would be better to make it customizable from settings
METRIC_TYPES = {
    'ETX': 'etx',
    'ETC': 'etc',
    'HOP': 'hop'
}

ID_TYPES = {
    'IPv4/v6': 1,
    'MAC': 2,
}

NETDIFF_PARSERS = getattr(settings, 'NODESHOT_NETDIFF_PARSERS', [
    ('netdiff.OlsrParser', 'Olsr (jsoninfo)'),
    ('netdiff.BatmanParser', 'Batman (Alfred)'),
    ('netdiff.BmxParser', 'Bmx6 (q6m)'),
    ('netdiff.NetJsonParser', 'Netjson (network-graph)'),
    ('netdiff.CnmlParser', 'CNML'),
])
