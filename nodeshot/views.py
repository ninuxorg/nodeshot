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
from utils import *
import time,re,os
import settings
from settings import DEBUG, NODESHOT_SITE as SITE
from django.core.exceptions import ObjectDoesNotExist
from forms import ContactForm, PasswordResetForm
from datetime import datetime, timedelta
from django.core.mail import EmailMessage

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

try:
    from settings import NODESHOT_LOG_CONTACTS as LOG_CONTACTS
except ImportError:
    LOG_CONTACTS = True

def index(request, slug=False):
    # retrieve statistics
    try:
        stat = Statistic.objects.latest('date')
        # round km
        stat.km = int(stat.km)
    except ObjectDoesNotExist:
        stat = False

    # default case for next code block
    gmap_center = NODESHOT_GMAP_CENTER
    # if node is in querystring we want to center the map somewhere else
    if slug:
        try:
            node = Node.objects.only('lat', 'lng').get(slug=slug)
            gmap_center = {
                # convert to string otherwise django might format the decimal separator with a comma, which would break gmap
                'is_default': 'false',
                'node': node.slug,
                'lat': str(node.lat),
                'lng': str(node.lng)
            }
        except ObjectDoesNotExist:
            # if node requested doesn't exist return 404
            raise Http404

    # prepare context
    context = {
        'stat': stat,
        'gmap_center': gmap_center
    }

    return render_to_response('index.html', context, context_instance=RequestContext(request))

def nodes(request):
    active = Node.objects.filter(status = 'a').values('name', 'slug', 'id', 'lng', 'lat')
    potential = Node.objects.filter(status = 'p').values('name', 'slug', 'id', 'lng', 'lat')
    hotspot = Node.objects.filter(status = 'h').values('name', 'slug', 'id', 'lng', 'lat')

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
    active = Node.objects.filter(status = 'a').values('name', 'slug', 'lng', 'lat').order_by('name')
    hotspot = Node.objects.filter(status = 'h').values('name', 'slug', 'lng', 'lat').order_by('name')
    potential = Node.objects.filter(status = 'p').values('name', 'slug', 'lng', 'lat').order_by('name')
    data, active_list, hotspot_list, potential_list = [], [], [], []

    for a in active:
        active_list.append({ 'data' : {'title' : a['name'], 'attr' : {'href' : 'javascript:mapGoTo(\'' + a['slug'] + '\')'} } })
    if len(active_list) > 0:
        data.append( { "data" : "Attivi", "state" : "open", "children" : list(active_list) } )

    for h in hotspot:
        hotspot_list.append({'data' :{'title' : h['name'], 'attr' : {'href' : 'javascript:mapGoTo(\'' + h['slug'] + '\')'} } })
    if len(hotspot_list) > 0:
        data.append( { "data" : "Hotspots", "state" : "open", "children" : list(hotspot_list) } )

    for p in potential:
        potential_list.append({'data' :{'title' : p['name'], 'attr' : {'href' : 'javascript:mapGoTo(\'' + p['slug'] + '\')'} } })
    if len(potential_list) > 0:
        data.append( { "data" : "Potenziali", "state" : "open", "children" : list(potential_list) } )

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def info_window(request, node_id):
    # vedere la class in models.py
    n = Node.objects.get(pk=node_id)
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
    data = data + [{'label': d.name, 'value': d.slug }  for d in Node.objects.filter(name__icontains=what).only('name','slug')]
    data = data + [{'label': d.ipv4_address , 'value': d.device.node.slug }  for d in Interface.objects.filter(ipv4_address__icontains=what).only('device__node__name')]
    data = data + [{'label': d.mac_address , 'value': d.device.node.slug }  for d in Interface.objects.filter(mac_address__icontains=what).only('device__node__name')]
    data = data + [{'label': d.ssid , 'value': d.device.node.slug }  for d in Interface.objects.filter(ssid__icontains=what).only('device__node__name')]
    if len(data) > 0:
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
    for d in Device.objects.all().order_by('node__status').select_related().only('name', 'type', 'node__name', 'node__status'):
        entry['status'] = "on" if d.node.status == 'a' else "off"
        entry['device_type'] = d.type
        entry['node_name'] = d.node.name
        entry['name'] = d.name
        entry['ips'] = [ip['ipv4_address'] for ip in d.interface_set.values('ipv4_address')] if d.interface_set.count() > 0 else ""
        entry['macs'] = [mac['mac_address'] if mac['mac_address'] != None else '' for mac in d.interface_set.values('mac_address')] if d.interface_set.count() > 0 else ""
        # heuristic count for good representation of the signal bar (from 0 to 100)
        #entry['signal_bar'] = signal_to_bar(d.max_signal)  if d.max_signal < 0 else 0
        #entry['signal'] = d.max_signal
        links = Link.objects.filter(from_interface__device = d).select_related().only('dbm', 'to_interface__mac_address', 'to_interface__device__node__name')
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

    return render_to_response(template,{'devices': devices}, context_instance=RequestContext(request))

def contact(request, node_id):
    ''' Form to contact node owners '''
    # if request is sent with ajax
    if request.is_ajax():
        # just load the fragment
        template = 'ajax/contact.html'
    # otherwise if request is sent normally and DEBUG is true
    elif DEBUG:
        # debuggin template
        template = 'contact.html'
    else:
        raise Http404
    
    # retrieve object or return 404 error
    try:
        node = Node.objects.only('name', 'email', 'email2', 'email3', 'status').get(pk=node_id)
    except ObjectDoesNotExist:
        raise Http404
    # if node is unconfirmed return 404 error
    if node.status == 'u':
        raise Http404

    # message has not been sent yet
    sent = False

    # if form has been submitted
    if request.method == 'POST':
        # http referer
        http_referer = request.POST.get('http_referer')
        # save extra information in a dictionary that we'll pass to the form
        extra = {
            'node': node_id,
            # add extra info about the sender
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE')
        }

        # init form and pass extra values to it
        form = ContactForm(extra, request.POST)
        # proceed in sending email only if form is valid
        if form.is_valid():
            # prepare to list
            to = [node.email]
            # if node has an second email address specified include it in the cc
            if node.email2 != '' and node.email2 != None:
                to += [node.email2]
            # if node has a third email address specified include it in the cc
            if node.email3 != '' and node.email3 != None:
                to += [node.email3]
            # prepare context
            context = {
                'node': node,
                'sender': {
                    'from_name': request.POST.get('from_name'),
                    'from_email': request.POST.get('from_email'),
                    'message': request.POST.get('message'),
                },
                'site': SITE
            }
            # parse subject
            subject = render_to_string('email_notifications/contact_node_subject.txt',context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            # parse message
            message = render_to_string('email_notifications/contact_node_body.txt',context)
            # prepare EmailMessage object, we are using this one because we want to send one mail only with other eventual owners in CC so they can hit reply to all button easily
            email = EmailMessage(subject, message, to=to, headers = {'Reply-To': request.POST.get('from_name')})
            email.send()
            sent = True
            # if enabled from settings
            if LOG_CONTACTS:
                # save log into database
                new_log = form.save()

    # if form has NOT been submitted
    else:
        form = ContactForm()
        http_referer = request.META.get('HTTP_REFERER')

    context = {
        'sent': sent,
        'node': node,
        'form': form,
        'http_referer': http_referer
    }

    return render_to_response(template, context, context_instance=RequestContext(request))
    
def recover_password(request, node_id):
    # if request is sent with ajax
    if request.is_ajax():
        # just load the fragment
        template = 'ajax/recover_password.html'
    # otherwise if request is sent normally and DEBUG is true
    elif DEBUG:
        # debuggin template
        template = 'recover_password.html'
    else:
        raise Http404
    
    # retrieve object or return 404 error
    try:
        node = Node.objects.only('name', 'email', 'email2', 'email3', 'status').get(pk=node_id)
    except ObjectDoesNotExist:
        raise Http404
    # if node is unconfirmed return 404 error
    if node.status == 'u':
        raise Http404
    
    # default value for sent variable
    sent = False
    # default value for form
    form = PasswordResetForm(node)
    
    # if submitting the form
    if request.method == 'POST':
        email = request.POST.get('email')
        # prepare custom dictionary to pass to the form, we need to pass the node object to verify the email and avoid querying the database twice.
        values = {
            'email': email,
            'node_email1': node.email,
            'node_email2': node.email2,
            'node_email3': node.email3
        }
        # init form with POST values
        form = PasswordResetForm(node, request.POST)
        # validate the form
        if form.is_valid():
            new_password = node.reset_password(email)
            sent = True
    
    context = {
        'sent': sent,
        'node': node,
        'form': form,
    }
    
    return render_to_response(template, context, context_instance=RequestContext(request))

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
    if not returns a 404 http status code
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
    This view might be called with a cron so the purging can be done automatically.
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