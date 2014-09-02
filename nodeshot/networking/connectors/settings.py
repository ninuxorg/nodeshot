from django.conf import settings


NETENGINE_BACKENDS = getattr(settings, 'NODESHOT_NETENGINE_BACKENDS', [
    ('netengine.backends.ssh.AirOS', 'AirOS (SSH)'),
    ('netengine.backends.ssh.OpenWRT', 'OpenWRT (SSH)'),
    ('netengine.backends.snmp.AirOS', 'AirOS (SNMP)'),
])
