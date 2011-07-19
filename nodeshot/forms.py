from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from nodeshot.models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import ModelForm
from django.core.exceptions import *
from django.forms.models import inlineformset_factory
from django.utils import simplejson
from django.db import models
from django import forms
from settings import DEBUG
from django.core.urlresolvers import reverse

def node_form(request):
    # add css classes
    class NodeForm(ModelForm):
        class Meta:
            model = Node 
        def __init__(self, *args, **kwargs):
            super(NodeForm, self).__init__(*args, **kwargs)
            for v in self.fields:
                self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'

    # retrieve node ID
    node_id = request.GET.get('id', None)

    # if form has been submitted
    if request.method == 'POST':
        # if a new node has been submitted
        if node_id == None:
            # return json: either errors or the redirect url
            form = NodeForm(request.POST)
            # if form is valid
            if form.is_valid():
                # prepare the node model object but don't save in the database yet
                node = form.save(commit=False)
                # save new node in the database (password encryption, activation_key and email notification is done in models.py)
                node.save()
                
                # if request is sent with ajax
                if request.is_ajax():
                    # return a blank page with node id
                    return HttpResponse(node.id)
                # otherwise if request is sent normally and DEBUG is true
                elif DEBUG:
                    # redirect to device form
                    return HttpResponseRedirect(reverse('nodeshot_device_form', args=[node.id]))
                # if in production return 404 as this should not happen
                else:
                    raise Http404
        # if changes to an existing node have been submitted
        else:
            # get object or return a 404
            node = get_object_or_404(Node, pk=node_id)
            # init the modelform object with the changes submitted
            form = NodeForm(request.POST, instance=node)
            # if form is valid
            if form.is_valid():
                # save
                form.save()
            
    # if form hasn't been submitted and we are going to edit an existing node
    elif request.method != 'POST' and node_id != None:
        # get object or return a 404
        node = get_object_or_404(Node, pk=node_id)
        # populate the form with the current node info
        form = NodeForm(instance=node)
    # if inserting a new node
    else:
        # blank form
        form = NodeForm()
    
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/node_form.html';
    else:
        # alternative mode available just for testing
        if DEBUG:
            template = 'node_form.html';
        else:
            raise Http404

    return render_to_response(template, { 'form' : form }, context_instance=RequestContext(request))

def device_form(request, node_id):    
    # get object or return a 404
    node = get_object_or_404(Node, pk=node_id)
    
    # init inlineformset_factory
    DeviceInlineFormSet = inlineformset_factory(Node, Device, extra=1)#, formfield_callback = my_formfield_cb)
    # init first formset
    formset = DeviceInlineFormSet(instance=node, prefix='devices')
    
    # if form has been submitted
    if request.method == "POST":
        # populate
        formset = DeviceInlineFormSet(request.POST, instance=node, prefix='devices')
        # if form is valid
        if formset.is_valid():
            # init list that will contain devices
            device_list = []
            # loop through devices
            for f in formset.forms:
                # save every device
                d = f.save()
                # append id to device_list
                device_list.append(str(d.id))
            # set response as a blank page with just the IDs of the devices separated by commas
            response = HttpResponse( ','.join(device_list))
            
    # else if form hasn't been submitted yet
    else:
        # set response with an empty form
        response = render_to_response("device_form.html", { "formset": formset, 'node_id': node_id }, context_instance=RequestContext(request))
    
    # return the response we've got in one of the previous cases
    return response

def configuration_form(request):
    device_id = request.GET.get('device_id', None)
    entry_type = request.GET.get('t', None)
    try:
        device = Device.objects.get(id=device_id)
    except:
        return HttpResponseNotFound('No such device id')

    if entry_type == "h4":
        mInlineFormSet = inlineformset_factory(Device, HNAv4, extra=1)#, formfield_callback = my_formfield_cb)
        template_form = "hnav4_form.html"
        prefix_name = 'hna4'
    elif entry_type == "if":
        mInlineFormSet = inlineformset_factory(Device, Interface, extra=1)#, formfield_callback = my_formfield_cb)
        template_form = "interface_form.html"
        prefix_name = 'interface'
    else:
        return HttpResponseNotFound('No type specified')

    if request.method == "POST":
        formset = mInlineFormSet(request.POST, instance=device, prefix=prefix_name)
        if formset.is_valid():
            for f in formset.forms:
                # only if the form is not empty
                if (entry_type == 'if' and f.data[f.prefix + "-ipv4_address"] == '' ) or (entry_type == 'h4' and f.data[f.prefix + "-route"] == '' ): 
                       pass # STUPID DJANGO, STUPID STUPID STUPID
                else:
                    f.save()
            return HttpResponse('ok')
    else:
        formset = mInlineFormSet(instance=device, prefix=prefix_name)
    return render_to_response(template_form, { "formset": formset , 'device_id': device_id , 'configuration_type': entry_type , 'description': device.name } )

