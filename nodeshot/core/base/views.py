from django.utils import timezone
from django.views.decorators.http import last_modified
from django.views.i18n import javascript_catalog
from django.views.decorators.cache import cache_page
from nodeshot import get_version

last_modified_date = timezone.now()

# The value returned by get_version() must change when translations change.
@cache_page(86400, key_prefix='js18n-%s' % get_version())
@last_modified(lambda req, **kw: last_modified_date)
def jsi18n(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)
