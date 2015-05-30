from django.shortcuts import render
from nodeshot.ui.default.settings import TILESERVER_URL


def open311(request):
    context = {
        'TILESERVER_URL': TILESERVER_URL
    }
    return render(request,'open311/index.html', context)
