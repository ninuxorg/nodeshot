from django.conf import settings

try:
    APPLICATION_PROTOCOLS = settings.NODESHOT['CHOICES']['APPLICATION_PROTOCOLS']
except KeyError:
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