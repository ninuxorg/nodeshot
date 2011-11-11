# nodeshot specific settings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

GMAP_CENTER = getattr(settings, 'NODESHOT_GMAP_CENTER', {'lat': '41.8934','lng': '12.4960'})
GMAP_CENTER['is_default'] = 'true'
SITE = getattr(settings, 'NODESHOT_SITE', False)
KML = getattr(settings, 'NODESHOT_KML', False)
ROUTING_PROTOCOLS = getattr(settings, 'NODESHOT_ROUTING_PROTOCOLS', (
    ('aodv','AODV'),
    ('batman','B.A.T.M.A.N.'),
    ('dsdv','DSDV'),
    ('dsr','DSR'),
    ('hsls','HSLS'),
    ('iwmp','IWMP'),
    ('olsr','OLSR'),
    ('oorp','OORP'),
    ('ospf','OSPF'),
    ('tora','TORA'),
))
DEFAULT_ROUTING_PROTOCOL = getattr(settings, 'NODESHOT_DEFAULT_ROUTING_PROTOCOL', 'olsr')
ACTIVATION_DAYS = getattr(settings, 'NODESHOT_ACTIVATION_DAYS', 7)
LOG_CONTACTS = getattr(settings, 'NODESHOT_LOG_CONTACTS', False)
# frontend settings
FRONTEND_SETTINGS = getattr(settings, 'NODESHOT_FRONTEND_SETTINGS', {})
HTML_TITLE_INDEX = FRONTEND_SETTINGS.get('HTML_TITLE_INDEX', _('Nodeshot, Open Source Map Server'))
META_ROBOTS = FRONTEND_SETTINGS.get('META_ROBOTS', 'noindex-nofollow')
SHOW_STATISTICS = FRONTEND_SETTINGS.get('SHOW_STATISTICS', True)
SHOW_KML_LINK = FRONTEND_SETTINGS.get('SHOW_KML_LINK', True)
HELP_URL = FRONTEND_SETTINGS.get('HELP_URL', 'http://wiki.ninux.org/UsareMapserver')
SHOW_ADMIN_LINK = FRONTEND_SETTINGS.get('SHOW_ADMIN_LINK', True)
TAB3 = FRONTEND_SETTINGS.get('TAB3', 'OLSR')
TAB4 = FRONTEND_SETTINGS.get('TAB4', 'VPN')
WELCOME_TEXT = FRONTEND_SETTINGS.get('WELCOME_TEXT', _('Welcome to Nodeshot!'))
LINK_QUALITY = FRONTEND_SETTINGS.get('LINK_QUALITY', 'etx')
del FRONTEND_SETTINGS

# this setting must be set to True by scripts in nodeshot/scripts/
#IS_SCRIPT = getattr(__builtins__, 'IS_SCRIPT', False)
# general
DEBUG = getattr(settings, 'DEBUG', True)
DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', False)

if 'staticgenerator.middleware.StaticGeneratorMiddleware' in settings.MIDDLEWARE_CLASSES:
    STATIC_GENERATOR = True
    try:
        WEB_ROOT = settings.WEB_ROOT
    except:
        raise ImproperlyConfigured(_('You must define WEB_ROOT in yout settings.py if you want staticgenerator to function properly.'))
else:
    STATIC_GENERATOR, WEB_ROOT = False, False

if not SITE:
    raise ImproperlyConfigured(_('NODESHOT_SITE is not defined in your settings.py. See settings.example.py for reference.'))

if not KML:
    raise ImproperlyConfigured(_('NODESHOT_KML is not defined in your settings.py. See settings.example.py for reference.'))
    
if not DEFAULT_FROM_EMAIL:
    raise ImproperlyConfigured(_('DEFAULT_FROM_EMAIL is not defined in your settings.py. See settings.example.py for reference.'))
    
if not settings.AUTH_PROFILE_MODULE:
    raise ImproperlyConfigured(_('AUTH_PROFILE_MODULE is not defined in your settings.py. See settings.example.py for reference.'))
    
if not settings.EMAIL_HOST:
    raise ImproperlyConfigured(_('EMAIL_HOST is not defined in your settings.py. See settings.example.py for reference.'))
    
if not settings.EMAIL_HOST_USER:
    raise ImproperlyConfigured(_('EMAIL_HOST_USER is not defined in your settings.py. See settings.example.py for reference.'))
    
if not settings.EMAIL_HOST_PASSWORD:
    raise ImproperlyConfigured(_('EMAIL_HOST_PASSWORD is not defined in your settings.py. See settings.example.py for reference.'))
    
if not settings.EMAIL_PORT:
    raise ImproperlyConfigured(_('EMAIL_HOST_PASSWORD is not defined in your settings.py. See settings.example.py for reference.'))