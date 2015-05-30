from django.conf import settings
from django.utils.translation import ugettext_lazy as _


LOGIN_TYPES = (
    (1, _('read-only')),
    (2, _('write')),
)

SERVICE_STATUS = (
    (1, _('up')),
    (2, _('down')),
    (3, _('not reachable'))
)

APPLICATION_PROTOCOLS = (
    ('http', 'http'),
    ('https', 'https'),
    ('ftp', 'FTP'),
    ('smb', 'Samba'),
    ('afp', 'AFP'),
    ('git', 'Git'),
)

TRANSPORT_PROTOCOLS = (
    ('tcp', 'TCP'),
    ('udp', 'UDP'),
)
