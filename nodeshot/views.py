# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import forms
from django.utils import simplejson
from django.core.context_processors import csrf
from nodeshot.models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import ModelForm
from django.core.exceptions import *
from utils import *
import time,re,os
import settings
from settings import DEBUG
from django.core.exceptions import ObjectDoesNotExist
#from forms import *
from datetime import datetime, timedelta

# retrieve map center or set default if not specified
try:
    from settings import NODESHOT_GMAP_CENTER
except ImportError:
    # default value is Rome - why? Because the developers of Nodeshot are based in Rome ;-)
    NODESHOT_GMAP_CENTER = {
        'lat': '41.90636538970964',
        'lng': '12.509307861328125'
    }
NODESHOT_GMAP_CENTER['is_default'] = 'true'

try:
    from settings import NODESHOT_ACTIVATION_DAYS
except ImportError:
    NODESHOT_ACTIVATION_DAYS = 7

def index(request):
    # retrieve statistics
    stat = Statistic.objects.latest('date')
    # round km
    stat.km = int(stat.km)
    # retrieve node in querystring, set False otherwise
    node = request.GET.get('node', False)
    # default case for next code block
    gmap_center = NODESHOT_GMAP_CENTER
    # if node is in querystring we want to center the map somewhere else
    if node:
        try:
            node = Node.objects.get(name=node)
            gmap_center = {
                # convert to string otherwise django might format the decimal separator with a comma, which would break gmap
                'is_default': 'false',
                'node': node.name,
                'lat': str(node.lat),
                'lng': str(node.lng)
            }
        except ObjectDoesNotExist:
            # if node requested doesn't exist fail silently and fall back on default NODESHOT_GMAP_CENTER value
            pass
    
    # prepare context
    context = {
        'stat': stat,
        'gmap_center': gmap_center
    }
    
    return render_to_response('index.html', context, context_instance=RequestContext(request))

def nodes(request):
    active = Node.objects.filter(status = 'a').values('name', 'lng', 'lat') 
    potential = Node.objects.filter(status = 'p').values('name', 'lng', 'lat')
    hotspot = Node.objects.filter(status = 'h').values('name', 'lng', 'lat')
    
    # retrieve links, select_related() reduces the number of queries, only() selects only the fields we need
    link_query = Link.objects.all().select_related().only(
        'from_interface__device__node__lat', 'from_interface__device__node__lng',
        'to_interface__device__node__lat', 'to_interface__device__node__lng',
        'to_interface__device__node__name', 'to_interface__device__node__name',
        'etx', 'dbm'
    )
    
    links = []
    for l in link_query:
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

    data = {'hotspot': list(hotspot), 'active': list(active), 'potential': list(potential), 'links': links} 
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
    info = {'node' : n, 'devices' : devices, 'nodes' : Node.objects.all().order_by('name')}
    
    
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
    
def confirm_node(request, node_id, activation_key):
    ''' Confirm node view '''
    # retrieve object or return 404 error
    node = get_object_or_404(Node, pk=node_id)
    
    if(node.activation_key != '' and node.activation_key != None):
        if(node.activation_key == activation_key):
            if(node.added + timedelta(days=NODESHOT_ACTIVATION_DAYS) > datetime.now()):
                # confirm node
                node.confirm()
                response = 'confirmed'
            else:
                response = 'expired'
        else:
            # wrong activation key
            response = 'wrong activation key'
    else:
        # node has been already confirmed
        response = 'node has been already confirmed'
    return HttpResponse(response)

def generate_kml(request):
    data = '''<kml xmlns="http://earth.google.com/kml/2.0">
    <Document>
    <name>%s</name>
    <description>%s Wireless Community</description>
    <LookAt>
        <longitude>12.48</longitude>
        <latitude>41.89</latitude>
        <range>100000</range>
        <tilt>0</tilt>
        <heading>0</heading>
    </LookAt>
    <Style id="activeNodeStyle">
        <IconStyle id="activeNodeIconStyle">
            <Icon>
                <href>%simages/marker_active.png</href>
            </Icon>
        </IconStyle>
    </Style>
    <Style id="potentialNodeStyle">
        <IconStyle id="potentialNodeIconStyle">
            <Icon>
                <href>%simages/marker_potential.png</href>
            </Icon>
        </IconStyle>
    </Style>
    <Style id="hotspotNodeStyle">
        <IconStyle id="hotspotNodeIconStyle">
            <Icon>
                <href>%simages/marker_hotspot.png</href>
            </Icon>
        </IconStyle>
    </Style>

    <Style id="Link1Style">
        <LineStyle>
            <color>7f00ff00</color>
            <width>4</width>
        </LineStyle>
    </Style>
    <Style id="Link2Style">
        <LineStyle>
            <color>7f00ffff</color>
            <width>4</width>
        </LineStyle>
    </Style>
    <Style id="Link3Style">
        <LineStyle>
            <color>7f0000ff</color>
            <width>4</width>
        </LineStyle>
    </Style>''' % (settings.ORGANIZATION, settings.ORGANIZATION, settings.MEDIA_URL, settings.MEDIA_URL, settings.MEDIA_URL )

    data += '''<Folder>
        <name>Active Nodes</name>
        <description>Nodes that are up and running</description>'''
    # active nodes
    for n in Node.objects.filter(status = 'a'):
        data = data + '''
            <Placemark>
                <name>''' + n.name + '''</name>
                <styleUrl>#activeNodeStyle</styleUrl>
                <Point><coordinates>''' + str(n.lng) + ',' + str(n.lat) + '''</coordinates></Point>
            </Placemark>  
        ''' 
    data += '</Folder>'

    data += '''<Folder>
        <name>Potential Nodes</name>
        <description>Potential node locations</description>'''
    # potential node
    for n in Node.objects.filter(status = 'p'):
        data = data + '''
            <Placemark>
                <name>''' + n.name + '''</name>
                <styleUrl>#potentialNodeStyle</styleUrl>
                <Point><coordinates>''' + str(n.lng) + ',' + str(n.lat) + '''</coordinates></Point>
            </Placemark>  
        ''' 
    data += '</Folder>'

    data += '''<Folder>
        <name>Potential Nodes</name>
        <description>Potential node locations</description>'''
    # hotspot node
    for n in Node.objects.filter(status = 'h'):
        data = data + '''
            <Placemark>
                <name>''' + n.name + '''</name>
                <styleUrl>#hotspotNodeStyle</styleUrl>
                <Point><coordinates>''' + str(n.lng) + ',' + str(n.lat) + '''</coordinates></Point>
            </Placemark>  
        ''' 
    data += '</Folder>'

    data += '''<Folder>
        <name>Links</name>
        <description>Radio Wireless Links and their quality</description>'''
    # links 
    for l in Link.objects.all():
        quality = 0
        if 0 < l.etx < 1.5:
           quality = 1
        elif l.etx < 3:
           quality = 2
        else:
           quality = 3

        data = data + '''
        <Placemark>
        <name>''' + l.from_interface.device.node.name + '-' + l.to_interface.device.node.name + ' ETX ' + str(l.etx) + '''</name>
        <styleUrl>#Link''' + str(quality) + '''Style</styleUrl>
            <LineString>
              <coordinates>''' + str(l.from_interface.device.node.lng) + ',' + str(l.from_interface.device.node.lat) + ' ' + str(l.to_interface.device.node.lng) + ',' + str(l.to_interface.device.node.lat) + '''</coordinates> 
            </LineString>
        </Placemark>
        '''
    data += '</Folder>'

    data += '''
        </Document>
    </kml>'''
    return HttpResponse(data)

def report_abuse(request, node_id, email):
    '''
    Checks if a node with specified id and email exist
    if yes sends an email to the administrators to report the abuse
    if not it returns a 404 http status code
    '''
    # retrieve object or return 404 error
    node = get_object_or_404(Node, pk=node_id)
    if(node.email != email and node.email2 != email and node.email3 != email):
        raise Http404
    
    try:
        from settings import NODESHOT_SITE
    except ImportError:
        raise ImproperlyConfigured('NODESHOT_SITE is not defined in your settings.py. See settings.example.py for reference.')
    
    context = {
        'email': email,
        'node': node,
        'site': NODESHOT_SITE
    }
    notify_admins(node, 'email_notifications/report_abuse_subject.txt', 'email_notifications/report_abuse_body.txt', context)
    
    return HttpResponse('reported')
    
def purge_expired(request):
    '''
    Purge all the nodes that have not been confirmed older than settings.NODESHOT_ACTIVATION_DAYS.
    This view might be called with a cron so the purging would be done automatically.
    '''
    # select unconfirmed nodes which are older than NODESHOT_ACTIVATION_DAYS
    nodes = Node.objects.filter(status='u', added__lt=datetime.now() - timedelta(days=NODESHOT_ACTIVATION_DAYS))
    # if any old unconfirmed node is found
    if len(nodes)>0:
        # prepare empty list that will contain the purged nodes
        response = ''
        # loop over nodes
        for node in nodes:
            response += '%s<br />' % node.name
            node.delete()
        response = 'The following nodes have been purged:<br /><br />' + response
    else:
        response = 'There are no old nodes to purge.'
        
    return HttpResponse(response)
