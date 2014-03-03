from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

def map_view(request):
    if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
        context = {'participation': True}
    else:
        context = {'participation': False}
    return render(request,'interface/index.html',context)

def request_view(request,*args,**kwargs):
    request_id = kwargs['request_id']
    if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
        context = {'request_id':request_id,'participation': True}
    else:
        context = {'request_id':request_id,'participation': False}
    return render(request,'interface/request.html',context)
