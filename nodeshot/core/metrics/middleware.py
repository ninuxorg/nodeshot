import inspect
import time

from tld import get_tld
from tld.exceptions import TldBadUrl, TldDomainNotFound, TldIOError

from .utils import write
from . import settings


class InfluxDBRequestMiddleware(object):
    """
    Measures request time and sends metric to InfluxDB.
    Credits go to: https://github.com/andymckay/django-statsd/blob/master/django_statsd/middleware.py#L24  # NOQA
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        view = view_func
        if not inspect.isfunction(view_func):
            view = view.__class__
        try:
            request._view_module = view.__module__
            request._view_name = view.__name__
            request._start_time = time.time()
        except AttributeError:  # pragma: no cover
            pass

    def process_response(self, request, response):
        self._record_time(request)
        return response

    def process_exception(self, request, exception):
        self._record_time(request)

    def _record_time(self, request):
        if hasattr(request, '_start_time'):
            if request._view_module in settings.INFLUXDB_MIDDLEWARE_IGNORED_MODULES:
                return
            ms = int((time.time() - request._start_time) * 1000)
            if request.is_ajax():
                is_ajax = True
            else:
                is_ajax = False

            is_authenticated = False
            is_staff = False
            is_superuser = False
            if request.user.is_authenticated():
                is_authenticated = True
                if request.user.is_staff:
                    is_staff = True
                if request.user.is_superuser:
                    is_superuser = True

            referer = request.META.get('HTTP_REFERER')
            referer_tld = None
            referer_tld_string = ''
            if referer:
                try:
                    referer_tld = get_tld(referer, as_object=True)
                except (TldBadUrl, TldDomainNotFound, TldIOError):  # pragma: no cover
                    pass
            if referer_tld:
                referer_tld_string = referer_tld.tld
            # data
            values = {
                'response_time': ms,
                'is_ajax': is_ajax,
                'is_authenticated': is_authenticated,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
                'referer': str(referer),
                'referer_tld': referer_tld_string,
                'full_path': request.get_full_path()
            }
            # tags, for fast retrievals
            tags = {
                'method': request.method,
                'module': request._view_module,
                'view': request._view_name,
                'path': request.path
            }
            # write into db
            write(name='http_requests', values=values, tags=tags)
