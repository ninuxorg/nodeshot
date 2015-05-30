from django.conf import settings
from django.utils.translation import ugettext_lazy as _


OUTWARD_MAXLENGTH = getattr(settings, 'NODESHOT_MAILING_OUTWARD_MAXLENGTH', 9999)
OUTWARD_MINLENGTH = getattr(settings, 'NODESHOT_MAILING_OUTWARD_MINLENGTH', 50)
OUTWARD_SCHEDULING = getattr(settings, 'NODESHOT_MAILING_OUTWARD_SCHEDULING', (
    ('00', _('midnight')),
    ('04', _('04:00 AM')),
))
OUTWARD_HTML = getattr(settings, 'NODESHOT_MAILING_OUTWARD_HTML', True)
OUTWARD_STEP = getattr(settings, 'NODESHOT_MAILING_OUTWARD_STEP', 20)
OUTWARD_DELAY = getattr(settings, 'NODESHOT_MAILING_OUTWARD_DELAY', 10)

INWARD_REQUIRE_AUTH = getattr(settings, 'NODESHOT_MAILING_INWARD_REQUIRE_AUTH', True)
INWARD_MAXLENGTH = getattr(settings, 'NODESHOT_MAILING_INWARD_MAXLENGTH', 2000)
INWARD_MINLENGTH = getattr(settings, 'NODESHOT_MAILING_INWARD_MINLENGTH', 15)
INWARD_LOG = getattr(settings, 'NODESHOT_MAILING_INWARD_LOG', True)
