from django.conf import settings
from django.shortcuts import render

def map_view(request):
    if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
        context = {'participation': True}
    else:
        context = {'participation': False}
    return render(request,'interface/index.html',context)
