import datetime
from datetime import timedelta
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.utils import simplejson
from django.core.context_processors import csrf
from ns.models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import ModelForm
from django.core.exceptions import *
import time
import math
#from forms import *


def distance(origin, destination):
    'Haversine formula'
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


def index(request):
    max_radios = range(1,10)
    km = 0
    for l in Link.objects.all():
        km += distance((l.nodeA.lat,l.nodeA.lng), (l.nodeB.lat, l.nodeB.lng))
    km = '%0.3f' % km
    return render_to_response('index.html', {'max_radios': max_radios , 'active_n': Node.objects.filter(status = 'a').count() , 'potential_n': Node.objects.filter(status = 'p').count() , 'links_n': Link.objects.count(), 'km_n': km },context_instance=RequestContext(request))


def nodes(request):
   active = Node.objects.filter(status = 'a').values('name', 'lng', 'lat') 
   potential = Node.objects.filter(status = 'p').values('name', 'lng', 'lat') 
   links = []
   for l in Link.objects.all():
       entry = {'from_lng': l.nodeA.lng , 'from_lat': l.nodeA.lat, 'to_lng': l.nodeB.lng, 'to_lat': l.nodeB.lat, 'quality': l.quality}
       links.append(entry)
   data = {'active': list(active), 'potential': list(potential) , 'links': links} 
   return HttpResponse(simplejson.dumps(data), mimetype='application/json')


def node_list(request):
#    data = [
#            { 
#                "data" : "Roma", 
#                "state" : "open",
#                "children" : [ 
#                    {'data' : {"title" : "Fusolab", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Talamo", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Kiddy", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Lux", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Rustica-Salcito", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Nino", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Asello", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Clauz", "attr" : { "href" : "http://wiki.ninux.org" } } }, 
#                    {'data' : {"title" : "Fish", "attr" : { "href" : "http://wiki.ninux.org" } } }
#                    ]
#            },
#            { 
#                "data" : "Pisa", 
#                "state" : "open",
#                "children" : [ 
#                    {'data' : {"title" : "Eigenlab", "attr" : { "href" : "http://wiki.ninux.org" } } }
#                    ]
#            },
#            { 
#                "data" : "Mistretta", 
#                "state" : "open",
#                "children" : [ 
#                    {'data' : {"title" : "Boh", "attr" : { "href" : "http://wiki.ninux.org" } } }
#                    ]
#            },
#            { 
#                "data" : "Potenziali", 
#                "state" : "open",
#                "children" : [ 
#                    {'data' : {"title" : "Io", "attr" : { "href" : "http://wiki.ninux.org" } } }
#                    ]
#            },
#            ]
    
    active = Node.objects.filter(status = 'a').values('name', 'lng', 'lat') 
    potential = Node.objects.filter(status = 'p').values('name', 'lng', 'lat') 
    data = []
    active_list, potential_list = [] ,[] 

    for a in active:
        active_list.append({ 'data' : {'title' : a['name'], 'attr' : {'href' : 'javascript:mapGoTo(\'' + a['name'] + '\')'} } })
    if len(active_list) > 0:
        data.append( { "data" : "Attivi", "state" : "open", "children" : list(active_list) } )

    for p in potential:
        potential_list.append({'data' :{'title' : p['name'], 'attr' : {'href' : 'javascript:mapGoTo(\'' + p['name'] + '\')'} } })
    if len(potential_list) > 0:
        data.append( { "data" : "Potenziali", "state" : "open", "children" : list(potential_list) } )

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def info_window(request, nodeName):
    n = Node.objects.get(name = nodeName)
    info = {'node' : n}
    return render_to_response('info_window.html', info ,context_instance=RequestContext(request))

def info(request):
    devices = []
    entry = {}
    debug_signal = 40
    for d in Device.objects.all():
        entry['status'] = "on"
        entry['device_type'] = d.device_type.name 
        entry['node_name'] = d.node.name 
        entry['ip'] = d.interface_set.all()[0].ipv4_address if d.interface_set.count() > 0 else ""
        entry['mac'] = d.interface_set.all()[0].mac_address if d.interface_set.count() > 0 else ""
        entry['signal'] = debug_signal   
        debug_signal += 1
        devices.append(entry)
        entry = {}
    return render_to_response('info.html',{'devices': devices} ,context_instance=RequestContext(request))
