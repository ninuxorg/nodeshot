# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.utils import simplejson
from django.core.context_processors import csrf
from nodeshot.models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import ModelForm
from django.core.exceptions import *
from django.db.models import Q
from utils import *
import time,re,os
from settings import DEBUG
#from forms import *

def index(request):
    max_radios = range(1,10)
    km = 0
    for l in Link.objects.all():
        km += distance((l.from_interface.device.node.lat,l.from_interface.device.node.lng), (l.to_interface.device.node.lat, l.to_interface.device.node.lng))
    km = '%0.3f' % km
    return render_to_response('index.html', {'max_radios': max_radios , 'active_n': Node.objects.filter(status = 'a').count() , 'potential_n': Node.objects.filter(status = 'p').count() , 'links_n': Link.objects.count(), 'km_n': km },context_instance=RequestContext(request))


def nodes(request):
   active = Node.objects.filter(status = 'a').values('name', 'lng', 'lat') 
   potential = Node.objects.filter(status = 'p').values('name', 'lng', 'lat') 
   links = []
   for l in Link.objects.all():
       etx = 0
       if 0 < l.etx < 1.5:
           etx = 1
       elif l.etx < 3:
           etx = 2
       else:
           etx = 3

       if -60 < l.dbm < 0:
            dbm = 1
       elif l.dbm > -75:
            dbm = 2
       else:
            dbm = 3

       entry = {'from_lng': l.from_interface.device.node.lng , 'from_lat': l.from_interface.device.node.lat, 'to_lng': l.to_interface.device.node.lng, 'to_lat': l.to_interface.device.node.lat, 'etx': etx , 'dbm': dbm }
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
    # vedere la class in models.py
    n = Node.objects.get(name = nodeName)
    # https://docs.djangoproject.com/en/dev/topics/db/queries/#following-relationships-backward
    devices = n.device_set.select_related().all()
    # interfaces=[]
    # for device in devices:
    #    interfaces.append(device.interface_set.all())
        
    # i= Interface.objects.get(device = d)
    info = {'node' : n, 'devices' : devices}
    
    
    return render_to_response('info_window.html', info, context_instance=RequestContext(request))

def search(request, what):
    data = []
    data = data + [{'label': d.name, 'value': d.name }  for d in Node.objects.filter(Q(name__icontains=what))]
    data = data + [{'label': d.ipv4_address , 'value': d.device.node.name }  for d in Interface.objects.filter(ipv4_address__icontains=what)]
    data = data + [{'label': d.mac_address , 'value': d.device.node.name }  for d in Interface.objects.filter(mac_address__icontains=what)]
    data = data + [{'label': d.ssid , 'value': d.device.node.name }  for d in Interface.objects.filter(ssid__icontains=what)]
    if len(data) > 0:
        #data = [{'label': d['name'], 'value': d['name']}  for d in data]
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    else:
        return HttpResponse("", mimetype='application/json')

def generate_rrd(request):
    ip = request.GET.get('ip', None)
    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    if re.match(pattern, ip):
        os.system("/home/ninux/nodeshot/scripts/ninuxstats/create_rrd_image.sh " + ip + " > /dev/null")
        return  render_to_response('rrd.html', {'filename' : ip + '.png' } ,context_instance=RequestContext(request))
    else:
        return HttpResponse('Error')

def info(request):
    devices = []
    entry = {}
    for d in Device.objects.all().order_by('node__status'):
        entry['status'] = "on" if d.node.status == 'a' else "off"
        entry['device_type'] = d.type
        entry['node_name'] = d.node.name 
        entry['name'] = d.name 
        entry['ips'] = [ip['ipv4_address'] for ip in d.interface_set.values('ipv4_address')] if d.interface_set.count() > 0 else ""
        entry['macs'] = [mac['mac_address'] if mac['mac_address'] != None else '' for mac in d.interface_set.values('mac_address')] if d.interface_set.count() > 0 else ""
        # heuristic count for good representation of the signal bar (from 0 to 100)
        #entry['signal_bar'] = signal_to_bar(d.max_signal)  if d.max_signal < 0 else 0
        #entry['signal'] = d.max_signal  
        links = Link.objects.filter(from_interface__device = d)
        # convert QuerySet in list
        links = list(links)
        for l in links:
            l.signal_bar = signal_to_bar(l.dbm) if l.to_interface.mac_address not in  entry['macs'] else links.remove(l)
        entry['links'] = links 
        entry['ssids'] = [ssid['ssid'] for ssid in d.interface_set.values('ssid')] if d.interface_set.count() > 0 else ""
        entry['nodeid'] = d.node.id
        devices.append(entry)
        entry = {}
    
    # if request is sent with ajax
    if request.is_ajax():
        # just load the fragment
        template = 'ajax/info.html'
    # otherwise if request is sent normally and DEBUG is true
    elif DEBUG:
        # debuggin template
        template = 'info.html'
    else:
        raise Http404
    
    return render_to_response('info.html',{'devices': devices} ,context_instance=RequestContext(request))
