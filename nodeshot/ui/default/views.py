from django.conf import settings
from django.shortcuts import render

from nodeshot.core.layers.models import Layer


def index(request):
    context = {
        'layers': Layer.objects.published()
    }
    return render(request, 'index.html', context)
