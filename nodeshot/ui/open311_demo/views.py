from django.conf import settings
from django.shortcuts import render

def open311(request):
    context = {
        'TILESERVER_URL': settings.NODESHOT['SETTINGS'].get('TILESERVER_URL', '//a.tiles.mapbox.com/v3/nodeshot-cineca.i6kgg4hb/{z}/{x}/{y}.png')
    }
    return render(request,'open311/index.html', context)


