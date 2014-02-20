from django.test.client import FakePayload, MULTIPART_CONTENT
from django.test.client import Client as BaseClient
from django.test import TestCase
from django.conf import settings

from urlparse import urlparse, urlsplit


if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    user_fixtures = 'test_profiles.json'
else:
    user_fixtures = 'test_users.json'


### --- Add patch method, for Django < 1.5 --- ###


class Client(BaseClient):
    """
    Construct a second test client which can do PATCH requests.
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PATCH request."
 
        patch_data = self._encode_data(data, content_type)
 
        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(patch_data),
        }
        r.update(extra)
        return self.request(**r)


class BaseTestCase(TestCase):
    """
    Test case with a client that can do patch requests
    """
    
    client_class = Client