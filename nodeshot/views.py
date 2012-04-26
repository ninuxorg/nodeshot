# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from nodeshot.forms import InterfaceInlineFormset
from django.utils import simplejson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from nodeshot.models import *
from nodeshot.forms import *
from nodeshot.utils import signal_to_bar, distance, email_owners, jslugify
from datetime import datetime, timedelta
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from settings import *

if DEBUG:
    import logging

def index(request, slug=False):
    """
    Home of the map-server. Google Maps and all that stuff ;-)
    """
    # retrieve statistics
    try:
        stat = Statistic.objects.latest('date')
        # round km
        stat.km = int(stat.km)
    except ObjectDoesNotExist:
        stat = False

    # default case for next code block
    gmap_config = GMAP_CONFIG
    # if node is in querystring we want to center the map somewhere else
    if slug:
        try:
            node = Node.objects.only('lat', 'lng', 'slug','status').get(slug=slug)
            gmap_config = {
                'is_default': 'false',
                'node': '%s;%s' % (jslugify(node.slug), node.status),
                # convert to string otherwise django might format the decimal separator with a comma, which would break gmap
                'lat': str(node.lat),
                'lng': str(node.lng)
            }
        except ObjectDoesNotExist:
            # if node requested doesn't exist return 404
            raise Http404

    # prepare context
    context = {
        'stat': stat,
        'gmap_config': gmap_config,
        'settings': {
            'HTML_TITLE_INDEX': HTML_TITLE_INDEX,
            'META_ROBOTS': META_ROBOTS,
            'SHOW_STATISTICS': SHOW_STATISTICS,
            'SHOW_KML_LINK': SHOW_KML_LINK,
            'HELP_URL': HELP_URL,
            'SHOW_ADMIN_LINK': SHOW_ADMIN_LINK,
            'TAB3': TAB3,
            'TAB4': TAB4,
            'WELCOME_TEXT': WELCOME_TEXT,
            'LINK_QUALITY': LINK_QUALITY
        },
        'DEBUG': DEBUG
    }

    return render_to_response('index.html', context, context_instance=RequestContext(request))

def nodes(request):
    """
    Returns a json list with all the nodes divided in active, potential and hostspot
    Populates javascript object nodeshot.nodes
    """
    # retrieve nodes in 3 different objects depending on the status
    active = Node.objects.filter(status = 'a').values('name', 'slug', 'id', 'lng', 'lat', 'status')
    # status ah (active & hotspot) will fall in the hotspot group, having the hotspot icon
    hotspot = Node.objects.filter(Q(status = 'h') | Q(status = 'ah')).values('name', 'slug', 'id', 'lng', 'lat', 'status')
    potential = Node.objects.filter(status = 'p').values('name', 'slug', 'id', 'lng', 'lat', 'status')

    # retrieve links, select_related() reduces the number of queries,
    # only() selects only the fields we need
    # double underscore __ indicates that we are following a foreign key
    link_queryset = Link.objects.all().exclude(hide=True).select_related().only(
        'from_interface__device__node__lat', 'from_interface__device__node__lng',
        'to_interface__device__node__lat', 'to_interface__device__node__lng',
        'to_interface__device__node__name', 'to_interface__device__node__name',
        'etx', 'dbm'
    )
    # evaluate queryset
    
    # prepare empty list
    links = []
    # loop over queryset (remember: evaluating queryset makes query to the db)
    for l in link_queryset:
        # determining link colour (depending on link quality)
        etx = l.get_quality('etx')
        dbm = l.get_quality('dbm')
        # prepare result
        entry = {
            'from_lng': l.from_interface.device.node.lng ,
            'from_lat': l.from_interface.device.node.lat,
            'to_lng': l.to_interface.device.node.lng,
            'to_lat': l.to_interface.device.node.lat,
            # raw values
            'retx': l.etx,
            'rdbm': l.dbm,
            # interpreted values (link quality, can be 1, 2 or 3)
            'etx': etx,
            'dbm': dbm
        }
        # append/push result into list
        links.append(entry)
    
    #prepare data for json serialization
    active_nodes, hotspot_nodes, potential_nodes = {}, {}, {}
    for node in active:
        node['jslug'] = jslugify(node['slug'])
        active_nodes[jslugify(node['slug'])] = node
    for node in hotspot:
        node['jslug'] = jslugify(node['slug'])
        hotspot_nodes[jslugify(node['slug'])] = node
    for node in potential:
        node['jslug'] = jslugify(node['slug'])
        potential_nodes[jslugify(node['slug'])] = node
    data = {
        'active': active_nodes,
        'hotspot': hotspot_nodes,        
        'potential': potential_nodes,
        'links': links
    }
    # return json
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def jstree(request):
    """
    Populates jquery.jstree plugin
    """
    # retrieve nodes in 3 different objects depending on the status
    active = Node.objects.filter(Q(status = 'a') | Q(status = 'ah')).values('name', 'slug', 'lng', 'lat', 'status').order_by('name') # status is necessary to link "active & hotspot" nodes correctly
    hotspot = Node.objects.filter(Q(status = 'h') | Q(status = 'ah')).values('name', 'slug', 'lng', 'lat').order_by('name')
    potential = Node.objects.filter(status = 'p').values('name', 'slug', 'lng', 'lat').order_by('name')
    # prepare empty lists
    data, active_list, hotspot_list, potential_list = [], [], [], []

    for a in active:
        # distinguish "active" from "active & hotspot"
        if a['status'] == 'a':
            status = 'active'
        elif a['status'] == 'ah':
            # treat "active & hotspot" like hotspots
            status = 'hotspot'
        
        active_list.append({
            'data': {
                'title': a['name'],
                'attr': {
                    'class': 'child',
                    'href': 'javascript:nodeshot.gmap.goToNode(nodeshot.nodes.%s.%s)' % (status, jslugify(a['slug']))
                }
            }
        })
    if len(active_list) > 0:
        data.append({
            'data': ugettext('Active Nodes'),
            'state': 'open',
            'attr': {
                'class': 'active_nodes',
            },
            'children': list(active_list)
        })

    for h in hotspot:
        hotspot_list.append({
            'data': {
                'title': h['name'],
                'attr': {
                    'class': 'child',
                    'href': 'javascript:nodeshot.gmap.goToNode(nodeshot.nodes.hotspot.%s)' % jslugify(h['slug'])
                }
            }
        })
    if len(hotspot_list) > 0:
        data.append({
            'data': ugettext('Hotspots'),
            'state': 'open',
            'attr': {
                'class': 'hotspot_nodes'
            },
            'children': list(hotspot_list)
        })

    for p in potential:
        potential_list.append({
            'data': {
                'title': p['name'],
                'attr': {
                    'class': 'child',
                    'href': 'javascript:nodeshot.gmap.goToNode(nodeshot.nodes.potential.%s)' % jslugify(p['slug'])
                }
            }
        })
    if len(potential_list) > 0:
        data.append({
            'data': ugettext('Potential Nodes'),
            'state': 'open',
            'attr': {
                'class': 'potential_nodes'
            },
            'children': list(potential_list)
        })
    # return json
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    
def search(request, what):
    data = []
    data = data + [{'label': n.name, 'value': jslugify(n.slug), 'slug': n.slug, 'name': n.name, 'lat': n.lat, 'lng': n.lng, 'status': n.status }  for n in Node.objects.filter(name__icontains=what).exclude(status='u').only('name','slug','lat','lng','status')]
    data = data + [{'label': d.name, 'value': jslugify(d.node.slug), 'slug': d.node.slug, 'name': d.node.name, 'lat': d.node.lat, 'lng': d.node.lng, 'status': d.node.status }  for d in Device.objects.filter(name__icontains=what).only('name','node__name','node__slug','node__lat','node__lng','node__status')]
    data = data + [{'label': i.ipv4_address , 'value': jslugify(i.device.node.slug), 'slug': i.device.node.slug, 'name': i.device.node.name, 'lat': i.device.node.lat, 'lng': i.device.node.lng, 'status': i.device.node.status }  for i in Interface.objects.filter(ipv4_address__icontains=what).only('device__node__name','device__node__slug','device__node__lat','device__node__lng','status')]
    data = data + [{'label': i.ipv6_address , 'value': jslugify(i.device.node.slug), 'slug': i.device.node.slug, 'name': i.device.node.name, 'lat': i.device.node.lat, 'lng': i.device.node.lng, 'status': i.device.node.status }  for i in Interface.objects.filter(ipv6_address__icontains=what).only('device__node__name','device__node__slug','device__node__lat','device__node__lng','status')]
    data = data + [{'label': i.mac_address , 'value': jslugify(i.device.node.slug), 'slug': i.device.node.slug, 'name': i.device.node.name, 'lat': i.device.node.lat, 'lng': i.device.node.lng, 'status': i.device.node.status }  for i in Interface.objects.filter(mac_address__icontains=what).only('device__node__name','device__node__slug','device__node__lat','device__node__lng','status')]
    # I think this is useless cos all our devices have ssid: ninux.org
    #data = data + [{'label': d.ssid , 'value': jslugify(d.device.node.slug), 'slug': d.device.node.slug, 'name': d.device.node.name, 'lat': d.device.node.lat, 'lng': d.device.node.lng, 'status': d.device.node.status }  for d in Interface.objects.filter(ssid__icontains=what).only('device__node__name','device__node__slug','device__node__lat','device__node__lng','status')]
    if len(data) > 0:
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    else:
        return HttpResponse('{}', mimetype='application/json')

def overview(request):
    """
    Overview about the wireless network. Device status and link performance for the entire network.
    This is quite database expensive. Use with caution. Needs caching.
    """
    # load always frament only
    template = 'ajax/overview.html'
    
    devices = Device.objects.all().order_by('node__name', 'added').select_related().only('name', 'type', 'node__name', 'node__status', 'node__slug');
    new_devices = []
    # loop over queryset
    for device in devices:
        entry = {}
        if device.node.status == 'a' or device.node.status == 'h':
            entry['status'] = 'on'
        else:
            entry['status'] = 'off'
            
        interfaces = device.interface_set.all().only('ipv4_address', 'mac_address', 'type')
            
        entry['device_type'] = device.type if device.type != None else ''
        entry['node'] = device.node
        entry['name'] = device.name
        
        ip_list = []
        macs_list = []
        for interface in interfaces:
            if interface.ipv4_address:
                ip_list.append(interface.ipv4_address)
            if interface.ipv6_address:
                ip_list.append(interface.ipv6_address)
            if not (interface.ipv4_address or interface.ipv6_address):
                ip_list.append(_('No ip specified'))
            if interface.mac_address != None and interface.mac_address != '':
                macs_list.append(interface.mac_address)
        entry['ips'] = ip_list
        entry['macs'] = macs_list
            
        #entry['ips'] = [ip['ipv4_address'] for ip in device.interface_set.values('ipv4_address')] if device.interface_set.count() > 0 else ""
        #entry['macs'] = [mac['mac_address'] if mac['mac_address'] != None else '' for mac in device.interface_set.values('mac_address')] if device.interface_set.count() > 0 else ""
        
        links = Link.objects.filter(
            Q(from_interface__device = device) | Q(to_interface__device = device)
        ).select_related().only(
            'dbm',
            'from_interface__mac_address',
            'from_interface__device__node__name',
            'from_interface__device__node__slug',
            'to_interface__mac_address',
            'to_interface__device__node__name',
            'to_interface__device__node__slug'            
        )
        # evaluate QuerySet
        links = list(links)
        for link in links:
            # if link is between same node skip
            if(link.to_interface.device.node.id == device.node.id and link.from_interface.device.node.id == device.node.id):
                if DEBUG: 
                    logging.log(1, 'duplicate for node %s' % device.node.name)
                links.remove(link)
                #continue
            if(link.from_interface.device.id == device.id):
                if link.to_interface.mac_address not in entry['macs']:
                    link.signal_bar = signal_to_bar(link.dbm)
                    link.destination = {
                        'name': link.to_interface.device.node.name,
                        'slug': link.to_interface.device.node.slug
                    }
                    
                else:
                    links.remove(link)
            elif(link.to_interface.device.id == device.id):
                if link.from_interface.mac_address not in entry['macs']:
                    link.signal_bar = signal_to_bar(link.dbm)
                    link.destination = {
                        'name': link.from_interface.device.node.name,
                        'slug': link.from_interface.device.node.slug
                    }
                else:
                    links.remove(link)
        
        entry['links'] = links
        #entry['ssids'] = [ssid['ssid'] for ssid in device.interface_set.values('ssid')] if device.interface_set.count() > 0 else ""
        new_devices.append(entry)    

    return render_to_response(template,{'devices': new_devices}, context_instance=RequestContext(request))
    
def node_info(request, node_id):
    """
    Content of nodeshot.gmap.infoWindow
    This view is requested asynchronously each time a marker is clicked
    """
    # if request is sent with ajax
    if request.is_ajax():
        # just load the fragment
        template = 'ajax/node_info.html'
    # otherwise if request is sent normally and DEBUG is true
    elif DEBUG:
        # debuggin template
        template = 'node_info.html'
    else:
        raise Http404
    
    # get object or raise 404
    try:
        node = Node.objects.exclude(status='u').only('id','name','slug','description','owner','postal_code','lat','lng','alt','status').get(pk=node_id)
    except ObjectDoesNotExist:
        raise Http404

    context = {'node': node, 'nodes': Node.objects.all().order_by('name').only('name','slug','lat','lng','status')}

    return render_to_response(template, context, context_instance=RequestContext(request))

def advanced(request, node_id):
    """
    Advanced information about a node.
    Loaded when clicking on the advanced tab after clicking on a marker.
    """
    # if request is sent with ajax
    if request.is_ajax():
        # just load the fragment
        template = 'ajax/advanced.html'
    # otherwise if request is sent normally and DEBUG is true
    elif DEBUG:
        # debuggin template
        template = 'advanced.html'
    else:
        raise Http404
    
    # retrieve object or return 404 error
    try:
        node = Node.objects.exclude(status='u').only('id','name','slug').get(pk=node_id)
    except ObjectDoesNotExist:
        raise Http404
    
    devices = Device.objects.filter(node=node_id)
    
    context = {
        'node': node,
        'devices': devices
    }
    
    return render_to_response(template, context, context_instance=RequestContext(request))

@csrf_exempt
def contact(request, node_id):
    """
    Displays a form to contact node owners
    """
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
        node = Node.objects.only('name', 'email', 'email2', 'email3', 'status').exclude(status='u').get(pk=node_id)
    except ObjectDoesNotExist:
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
            # prepare context
            context = {
                'node': node,
                'sender': {
                    'from_name': request.POST.get('from_name'),
                    'from_email': request.POST.get('from_email'),
                    'message': mark_safe(request.POST.get('message')),
                },
                'site': SITE
            }
            # email owners
            email_owners(node, _('Contact request from %(sender)s - %(site)s') % {'sender':context['sender']['from_name'], 'site':SITE['name']}, 'email_notifications/contact-node-owners.txt', context, reply_to=request.POST.get('from_email'))
            # set sent to true
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

def extra_tab(request, tab):
    return render_to_response('tab%s.html' % tab, {}, context_instance=RequestContext(request))

def generate_kml(request):
    """
    Generates KML feed (Google Earth, ecc).
    """
    
    # retrieve nodes in 3 different objects depending on the status
    active = Node.objects.filter(status = 'a').only('name', 'lng', 'lat')
    hotspot = Node.objects.filter(Q(status = 'h') | Q(status = 'ah')).only('name', 'lng', 'lat')
    potential = Node.objects.filter(status = 'p').only('name', 'lng', 'lat')

    # retrieve links, select_related() reduces the number of queries,
    # only() selects only the fields we need
    # double underscore __ indicates that we are following a foreign key
    links = Link.objects.all().select_related().only(
        'from_interface__device__node__lat', 'from_interface__device__node__lng',
        'to_interface__device__node__lat', 'to_interface__device__node__lng',
        'to_interface__device__node__name', 'to_interface__device__node__name',
        'etx',
    )
    
    context = {
        'KML': KML,
        'GMAP_CONFIG': GMAP_CONFIG,
        'active': active,
        'hotspot': hotspot,
        'potential': potential,
        'links': links
    }
    
    return render_to_response('kml.xml', context, context_instance=RequestContext(request), mimetype='application/vnd.google-earth.kml+xml')
    
# this might be implemented in a future version
#def generate_rrd(request):
#    ip = request.GET.get('ip', None)
#    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
#    if re.match(pattern, ip):
#        os.system("/home/ninux/nodeshot/scripts/ninuxstats/create_rrd_image.sh " + ip + " > /dev/null")
#        return  render_to_response('rrd.html', {'filename' : ip + '.png' } ,context_instance=RequestContext(request))
#    else:
#        return HttpResponse('Error')

@csrf_exempt
def add_node(request):
    """
    Displays form to add a new node.
    """
    
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/add_node.html';
    else:
        # alternative mode available just for testing
        if DEBUG:
            template = 'add_node.html';
        else:
            raise Http404

    # if form has been submitted
    if request.method == 'POST':
        # return json: either errors or the redirect url
        form = AddNodeForm(request.POST)
        # if form is valid
        if form.is_valid():
            # prepare the node model object but don't save in the database yet
            node = form.save(commit=False)
            # set node as unconfirmed, malicious users could edit the hidden input field easily with instruments like firebug.
            node.status = 'u'
            # generate slug
            # TODO: remove this because is being done at model level
            node.slug = slugify(node.name)
            # save new node in the database (password encryption, activation_key and email notification is done in models.py)
            node.save()
            # return a blank page with node id
            return HttpResponse(str(node.id))
    else:
        # blank form
        form = AddNodeForm()

    return render_to_response(template, { 'form' : form }, context_instance=RequestContext(request))

def confirm_node(request, node_id, activation_key):
    """
    Confirms a node with the specified ID and activation key.
    Handles different cases.
    """
    # retrieve object or return 404 error
    node = get_object_or_404(Node, pk=node_id)
    # redirect to url default
    redirect_to = reverse('nodeshot_index')

    if(node.activation_key != '' and node.activation_key != None):
        if(node.activation_key == activation_key):
            if(node.added + timedelta(days=ACTIVATION_DAYS) > datetime.now()):
                # confirm node
                node.confirm()
                message = _(u'Your new node has been confirmed successfully.')
                redirect_to = reverse('nodeshot_select', args=[node.slug])
            else:
                message = _(u'The activation key has expired.')
        else:
            # wrong activation key
            message = _(u'The activation key is wrong.')
    else:
        # node has been already confirmed
        message = _(u'Your new node has already been confirmed.')
        redirect_to = reverse('nodeshot_select', args=[node.slug])
    
    # message that will be displayed to the user 
    messages.add_message(request, messages.INFO, message)
        
    return HttpResponseRedirect(redirect_to)

def auth_node(request, node_id):
    """
    Authenticates user to edit a node.
    Authentication is method will be improved in future versions (if you wanna help, join us).
    """
    
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/auth_node.html';
    else:
        template = 'auth_node.html';
        
    # get object or raise 404
    try:
        node = Node.objects.select_related().exclude(status='u').get(pk=node_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # raw password to authenticate
    raw_password = request.POST.get('raw_password', False)
    # once authenticated password is sent in ecrypted format
    encrypted_password = request.POST.get('encrypted_password', False)
    # default value for authenticated variable
    authenticated = 0
    # init form
    form = EditNodeForm(instance=node)
    # default value for "saved" variable
    saved = False
    
    # if sending raw password check if is correct
    if raw_password and node.check_password(raw_password):
        authenticated = 1
        return HttpResponseRedirect(reverse('nodeshot_edit_node', args=[node_id, node.password]))
    # if password is not correct value of authenticated is 2
    elif raw_password and not node.check_password(raw_password):
        authenticated = 2
    # if password is being sent in encrypted format it means we are editing the form
    
    context = {
        'node': node,
        'authenticated': authenticated,
    }
    
    return render_to_response(template, context, context_instance=RequestContext(request))
    
def edit_node(request, node_id, password):
    """
    Displays the form to edit a node.
    """
        
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/edit_node.html';
    else:
        template = 'edit_node.html';
        
    # get object or raise 404
    try:
        node = Node.objects.select_related().exclude(status='u').get(pk=node_id, password=password)
    except ObjectDoesNotExist:
        raise Http404
    
    # default value for "saved" and "error" variables
    saved = False
    error = False
    
    # if form has been submitted
    if request.method == 'POST':
        # init edit form with POST values
        form = EditNodeForm(request.POST, instance=node)
        
        if form.is_valid():
            # get a Node object but don't save yet
            node = form.save(commit=False)
            # get new password or False
            new_password = request.POST.get('new_password', False)
            # if new password has been set
            if(new_password):
                # encrypt the new password
                node.password = new_password
                node.set_password()
                # encrypted_password now shall change to the new password
                encrypted_password = node.password
            # change slug
            node.slug = slugify(node.name)
            node.save()
            # this tells the template that the form has saved in order to display a message to the user
            saved = True
        else:
            error = True
    else:
        # init form
        form = EditNodeForm(instance=node)
    
    context = {
        'node': node,
        'form' : form,
        'saved': saved,
        'error': error
    }
    
    return render_to_response(template, context, context_instance=RequestContext(request))

def device_form(request, node_id, password):
    """
    Displays the form to edit devices of a node
    """
    
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/device_form.html';
    else:
        template = 'device_form.html';
        
    # get object or raise 404
    try:
        # get only name, status and password columns
        # don't consider unconfirmed or potential nodes
        # get node only if password is correct
        node = Node.objects.only('name', 'status', 'password').exclude(Q(status='u') & Q(status='p')).get(pk=node_id, password=password)
    except ObjectDoesNotExist:
        raise Http404
    
    # init inlineformset_factory
    modelFormSet = inlineformset_factory(Node, Device, formset=DeviceInlineFormset, extra=1)
    
    # default value for "saved" and "error" variables
    saved = False
    error = False
    # init formset
    formset = modelFormSet(instance=node, prefix='devices')
    
    # if form has been submitted
    if request.method == "POST":
        # populate
        formset = modelFormSet(request.POST, instance=node, prefix='devices')
        # if form is valid
        if formset.is_valid():
            # print a nice message in the template
            saved = True
            # loop through devices
            formset.save()
            # reset formset with new saved values
            formset = modelFormSet(instance=node, prefix='devices')
        else:
            # print a nice message in the template
            error = True
    
    context = {
        'formset': formset,
        'length': len(formset),
        'node': node,
        'node_id': node_id,
        'saved': saved,
        'error': error
    }
    
    # set response with an empty form
    return render_to_response(template, context, context_instance=RequestContext(request))
    
def configuration(request, node_id, password, type):
    """
    Displays form to edit interfaces or HNA.
    type argument is set at url config level.
    """
    
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/%s_form.html' % type;
    else:
        template = '%s_form.html' % type;
        
    # get object or raise 404
    try:
        # get only name, status and password columns
        # don't consider unconfirmed or potential nodes
        # get node only if password is correct
        node = Node.objects.only('name', 'status', 'password').exclude(Q(status='u') & Q(status='p')).get(pk=node_id, password=password)
    except ObjectDoesNotExist:
        raise Http404

    # retrieve devices
    devices = Device.objects.filter(node=node_id)

    # init formset factory
    if type == 'interface':
        modelFormSet = inlineformset_factory(Device, Interface, formset=InterfaceInlineFormset, extra=1)
    else:
        modelFormSet = inlineformset_factory(Device, Hna, extra=1)
    
    saved = False
    error = False
    # init variables for the loops
    objects = []
    # init counter
    i = 1
    
    # if submitting the form
    if request.method == "POST":
        # loop through devices
        for device in devices:
            # if this cycle has the device we submitted
            formset = modelFormSet(request.POST, instance=device, prefix='%s%s'%(type,i))
            if formset.is_valid():
                # save
                formset.save()
                # reload formset so it will show changes
                formset = modelFormSet(instance=device, prefix='%s%s'%(type,i))
            else:
                if DEBUG:
                    import logging
                    logging.log(1, dir(formset))
                error = True
            objects += [{'device': device, 'formset': formset }]
            i+=1
        # if no errors
        if not error:
            # print a nice message in the template
            saved = True    
    else:
        # just load initial data
        for device in devices:
            objects += [{'device': device, 'formset': modelFormSet(instance=device, prefix='%s%s'%(type,i))}]
            i+=1
    
    context = {
        'node': node,
        'type': type,
        'objects': objects,
        'saved': saved,
        'error': error
    }    
    
    return render_to_response(template, context, context_instance=RequestContext(request) )

def delete_node(request, node_id, password):
    """
    Deletes a node, requires password.
    """
        
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/delete_node.html';
    else:
        template = 'delete_node.html';
        
    # get object or raise 404
    try:
        node = Node.objects.select_related().exclude(status='u').get(pk=node_id, password=password)
    except ObjectDoesNotExist:
        raise Http404
    
    # if form has been submitted
    if request.method == 'POST':
        # prepare context
        email_context = {
            'node': node,
            'site': SITE
        }
        email_owners(node, _('Node %(node)s deleted') % {'node':node.name}, 'email_notifications/node-deleted-owners.txt', email_context)
        messages.add_message(request, messages.INFO, _(u'The node %(node)s has been deleted successfully.') % {'node':node.name})
        node.delete()
        
        return HttpResponseRedirect(reverse('nodeshot_index'))
    
    context = {
        'node': node,
    }
    
    return render_to_response(template, context, context_instance=RequestContext(request))
    
def report_abuse(request, node_id, email):
    """
    Checks if a node with specified id and email exist:
    if yes sends an email to the administrators to report the abuse;
    else returns a 404 http status code;
    """
    
    # retrieve object or return 404 error
    node = get_object_or_404(Node, pk=node_id)
    if(node.email != email and node.email2 != email and node.email3 != email):
        raise Http404

    context = {
        'email': email,
        'node': node,
        'site': SITE
    }
    notify_admins(node, _('Abuse reported for %(node)s') % {'node':SITE['name']}, 'email_notifications/report_abuse.txt', context)
    
    # message that will be displayed to the user 
    messages.add_message(request, messages.INFO, _(u"Thank you for reporting the abuse. We'll verify and come back to you as soon as possible."))
    
    return HttpResponseRedirect(reverse('nodeshot_index'))

@csrf_exempt  
def reset_password(request, node_id):
    """
    Displays a form to reset the password of a node.
    Requires email address (can be either node.email, node.email1 or node.email2).
    New password is sent via email to all the owners of the node.
    """
    
    # if request is sent with ajax
    if request.is_ajax():
        # just load the fragment
        template = 'ajax/reset_password.html'
    # otherwise if request is sent normally
    else:
        template = 'reset_password.html'
    
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

def purge_expired(request):
    """
    Purge all the nodes that have not been confirmed older than settings.ACTIVATION_DAYS.
    This view might be called with a cron so the purging can be done automatically.
    """
    
    # select unconfirmed nodes which are older than ACTIVATION_DAYS
    nodes = Node.objects.filter(status='u', added__lt=datetime.now() - timedelta(days=ACTIVATION_DAYS))
    # if any old unconfirmed node is found
    if len(nodes)>0:
        # prepare empty list that will contain the purged nodes
        response = ''
        # loop over nodes
        for node in nodes:
            response += '%s<br />' % node.name
            node.delete()
        response = 'The following unconfirmed nodes have been purged:<br /><br />' + response
    else:
        response = 'There are no old nodes to purge.'

    return HttpResponse(response)
