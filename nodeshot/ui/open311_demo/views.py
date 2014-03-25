from django.conf import settings
from django.shortcuts import render

def open311(request):
    return render(request,'open311/index.html')


