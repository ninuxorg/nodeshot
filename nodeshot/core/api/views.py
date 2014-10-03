from django.core.urlresolvers import NoReverseMatch

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .urls import urlpatterns


@api_view(('GET',))
def root_endpoint(request, format=None):
    """
    List of all the available resources of this RESTful API.
    """
    endpoints = []
    # loop over url modules
    for urlmodule in urlpatterns:
        # is it a urlconf module?
        if hasattr(urlmodule, 'urlconf_module'):
            is_urlconf_module = True
        else:
            is_urlconf_module = False
            
        # if url is really a urlmodule
        if is_urlconf_module:
            # loop over urls of that module
            for url in urlmodule.urlconf_module.urlpatterns:
                # TODO: configurable skip url in settings
                # skip api-docs url
                if url.name in ['django.swagger.resources.view']:
                    continue
                # try adding url to list of urls to show
                try:
                    endpoints.append({
                        'name': url.name.replace('api_', ''),
                        'url': reverse(url.name, request=request, format=format)
                    })
                # urls of object details will fail silently (eg: /nodes/<slug>/)
                except NoReverseMatch:
                    pass

    return Response(endpoints)
