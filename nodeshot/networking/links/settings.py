from django.conf import settings
from datetime import timedelta

DEFAULT_PARSERS = [
    ('netdiff.OlsrParser', 'OLSR (jsoninfo)'),
    ('netdiff.BatmanParser', 'batman-advanced (alfred-vis)'),
    ('netdiff.BmxParser', 'BMX6 (q6m)'),
    ('netdiff.NetJsonParser', 'NetJSON NetworkGraph'),
    ('netdiff.CnmlParser', 'CNML'),
]

PARSERS = DEFAULT_PARSERS + getattr(settings, 'NODESHOT_NETDIFF_PARSERS', [])

TOPOLOGY_UPDATE_INTERVAL = getattr(settings, 'NODESHOT_TOPOLOGY_UPDATE_INTERVAL', 3)

settings.CELERYBEAT_SCHEDULE.update({
    'update_topology': {
        'task': 'nodeshot.networking.links.tasks.update_topology',
        'schedule': timedelta(minutes=TOPOLOGY_UPDATE_INTERVAL),
    }
})
