from django.shortcuts import render_to_response
from django.template import RequestContext

from . import DOMAIN, PORT  # contained in __init__.py


def test(request):
    context = {
        'DOMAIN': DOMAIN,
        'PORT': PORT
    }
    return render_to_response('test.html', context,
                              context_instance=RequestContext(request))