
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
