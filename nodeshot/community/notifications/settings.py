from django.conf import settings
from django.utils.translation import ugettext_lazy as _


TEXTS = getattr(settings, 'NODESHOT_NOTIFICATIONS_TEXTS', {
    'custom': None,
    'node_created': _('A new node with name "%(name)s" has been created.'),
    'node_status_changed': _('Status of node "%(name)s" has changed from "%(old_status)s" to "%(new_status)s".'),
    'node_own_status_changed': _('Status of your node "%(name)s" changed from "%(old_status)s" to "%(new_status)s".'),
    'node_deleted': _('Node "%(name)s" with ID #%(id)s was deleted.'),
})
REGISTER = getattr(settings, 'NODESHOT_NOTIFICATIONS_REGISTER', ('nodeshot.community.notifications.registrars.nodes',))
# boolean: users can only turn on or off
# distance: users can turn off (-1), turn on for all (0) or set a range of km (n)
USER_SETTING = getattr(settings, 'NODESHOT_NOTIFICATIONS_USER_SETTING', {
    'node_created':             { 'type': 'distance', 'geo_field': 'geometry' },
    'node_status_changed':      { 'type': 'distance', 'geo_field': 'geometry' },
    'node_deleted':             { 'type': 'distance', 'geo_field': 'geometry' },
    'node_own_status_changed':  { 'type': 'boolean' },
})
DEFAULT_BOOLEAN = getattr(settings, 'NODESHOT_NOTIFICATIONS_DEFAULT_BOOLEAN', True)
DEFAULT_DISTANCE = getattr(settings, 'NODESHOT_NOTIFICATIONS_DEFAULT_DISTANCE', 30)
DELETE_OLD = getattr(settings, 'NODESHOT_NOTIFICATIONS_DELETE_OLD', 40)
