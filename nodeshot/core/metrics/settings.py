from django.utils.translation import ugettext as _
from django.conf import settings


RETENTION_POLICIES = getattr(settings, 'NODESHOT_METRICS_RETENTION_POLICIES', (
    ('%sd' % str(365 * 3), _('3 years')),
    ('%sd' % str(365 * 2), _('2 years')),
    ('%sd' % str(365 * 1), _('1 year')),
    ('%sd' % str(30 * 9), _('9 months')),
    ('%sd' % str(30 * 6), _('6 months')),
    ('%sd' % str(30 * 3), _('3 months')),
))

DEFAULT_RETENTION_POLICY = getattr(settings, 'NODESHOT_METRICS_DEFAULT_RETENTION_POLICY', RETENTION_POLICIES[0][0])

# mandatory
INFLUXDB_HOST = getattr(settings, 'INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = getattr(settings, 'INFLUXDB_PORT', '8086')
INFLUXDB_USER = getattr(settings, 'INFLUXDB_USER')
INFLUXDB_PASSWORD = getattr(settings, 'INFLUXDB_PASSWORD')
INFLUXDB_DATABASE = getattr(settings, 'INFLUXDB_DATABASE')
