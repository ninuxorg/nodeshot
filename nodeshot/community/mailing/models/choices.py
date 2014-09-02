from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.utils import choicify
from nodeshot.core.base.settings import ACCESS_LEVELS


__all__ = [
    'SCHEDULE_CHOICES',
    'FILTERING_CHOICES',
    'FILTER_CHOICES',
    'FILTERS',
    'OUTWARD_STATUS_CHOICES',
    'OUTWARD_STATUS',
    'GROUPS',
    'DEFAULT_GROUPS',
    'INWARD_STATUS_CHOICES'
]

SCHEDULE_CHOICES = (
    (0, _("Don't schedule, send immediately")),
    (1, _('Schedule')),
)

FILTERING_CHOICES = (
    (0, _('Send to all')),
    (1, _('Send accordingly to selected filters')),
)

FILTER_CHOICES = (
    (1, _('users of the selected groups')),
    (2, _('users which have a node in one of the selected layers')),
    (3, _('chosen users')),
)

# this is just for convenience and readability
FILTERS = {
    'groups': str(FILTER_CHOICES[0][0]),
    'layers': str(FILTER_CHOICES[1][0]),
    'users': str(FILTER_CHOICES[2][0])
}

OUTWARD_STATUS_CHOICES = (
    (-1, _('error')),
    (0, _('draft')),
    (1, _('scheduled')),
    (2, _('sent')),
    (3, _('cancelled'))
)

# this is just for convenience and readability
OUTWARD_STATUS = {
    'error': OUTWARD_STATUS_CHOICES[0][0],
    'draft': OUTWARD_STATUS_CHOICES[1][0],
    'scheduled': OUTWARD_STATUS_CHOICES[2][0],
    'sent': OUTWARD_STATUS_CHOICES[3][0],
    'cancelled': OUTWARD_STATUS_CHOICES[4][0]
}

GROUPS = []
DEFAULT_GROUPS = ''
# convert strings to integers
for group in choicify(ACCESS_LEVELS):
    GROUPS += [(int(group[0]), group[1])]
    DEFAULT_GROUPS += '%s,' % group[0]
GROUPS += [(0, _('super users'))]
DEFAULT_GROUPS += '0'

INWARD_STATUS_CHOICES = (
    (-1, _('Error')),
    (0, _('Not sent yet')),
    (1, _('Sent')),
    (2, _('Cancelled')),
)
