"""
OpenWISP OAuth support.
"""
from urllib import urlencode
import simplejson as json

from django.core.exceptions import ImproperlyConfigured

from social_auth.utils import dsa_urlopen
from social_auth.backends import BaseOAuth2, OAuthBackend

from ..settings import settings

# OpenWISP configuration
try:
    OPENWISP_BASE_URL = settings.OPENWISP_BASE_URL
except AttributeError:
    raise ImproperlyConfigured('missing settings.OPENWISP_BASE_URL')

OPENWISP_AUTHORIZATION_URL = '%s/oauth/authorize' % OPENWISP_BASE_URL
OPENWISP_ACCESS_TOKEN_URL = '%s/oauth/access_token' % OPENWISP_BASE_URL
OPENWISP_USER_DATA_URL = '%s/oauth/account_details.json' % OPENWISP_BASE_URL


class OpenWISPBackend(OAuthBackend):
    """OpenWISP OAuth authentication backend"""
    name = 'openwisp'
    # Default extra data to store
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_details(self, response):
        """Return user details from OpenWISP account"""
        return {
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
            'birth_date': response.get('birth_date'),
        }


class OpenWISPAuth(BaseOAuth2):
    """OpenWISP OAuth2 mechanism"""
    AUTHORIZATION_URL = OPENWISP_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = OPENWISP_ACCESS_TOKEN_URL
    AUTH_BACKEND = OpenWISPBackend
    SETTINGS_KEY_NAME = 'OPENWISP_APP_ID'
    SETTINGS_SECRET_NAME = 'OPENWISP_API_SECRET'
    SCOPE_SEPARATOR = ','
    SCOPE_VAR_NAME = 'OPENWISP_EXTENDED_PERMISSIONS'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = OPENWISP_USER_DATA_URL + '?' + urlencode({
            'access_token': access_token
        })

        try:
            data = json.load(dsa_urlopen(url))
        except ValueError:
            data = None

        return data

# Backend definition
BACKENDS = {
    'openwisp': OpenWISPAuth,
}
