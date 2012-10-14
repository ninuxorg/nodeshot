from django.conf import settings
from django.utils.translation import ugettext_lazy as _

try:
    AVAILABLE_CRONJOBS = settings.NODESHOT['CHOICES']['AVAILABLE_CRONJOBS']
except KeyError:
    AVAILABLE_CRONJOBS = (
        ('00', _('midnight')),
        ('04', _('04:00 AM')),
    )

SCHEDULE_CHOICES = (
    (0, _("Don't schedule, send immediately")),
    (1, _('Schedule')),
)

FILTERING_CHOICES = (
    (0, _('Send to all')),
    (1, _('Send accordingly to selected filters')),
)

FILTERS = (
    (1, _('users of the selected groups')),
    (2, _('users which have a node in one of the selected zones')),
    (3, _('chosen users')),
)

OUTWARD_STATUS = (
    (-1, _('error')),
    (0, _('draft')),
    (1, _('scheduled')),
    (2, _('sent')),
    (3, _('cancelled'))
)

GROUPS = []
DEFAULT_GROUPS = ''
# convert strings to integers
for group in settings.NODESHOT['CHOICES']['ACCESS_LEVELS']:
    GROUPS += [(int(group[0]), group[1])]
    DEFAULT_GROUPS += '%s,' % group[0]
GROUPS += [(0, _('super users'))]
DEFAULT_GROUPS += '0'

INWARD_STATUS = (
    (-1, _('Error')),
    (0, _('Not sent yet')),
    (1, _('Sent')),
    (2, _('Cancelled')),
)