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

RECIPIENT_TYPES = (
    (1, _('all users indistinctively')),
    (2, _('all the users which have a node in one of the selected zones')),
    (3, _('chosen users')),
)

OUTWARD_STATUS = (
    (-1, _('error')),
    (0, _('draft')),
    (1, _('scheduled')),
    (2, _('sent')),
    (3, _('cancelled'))
)

RECIPIENT_GROUPS = settings.NODESHOT['CHOICES']['ACCESS_LEVELS']
RECIPIENT_GROUPS += [('superusers', _('super users'))]

INWARD_STATUS = (
    (-1, _('Error')),
    (0, _('Not sent yet')),
    (1, _('Sent')),
    (2, _('Cancelled')),
)