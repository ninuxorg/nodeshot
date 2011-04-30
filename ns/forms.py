from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.context_processors import csrf
from ns.models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import ModelForm
from django.core.exceptions import *
from django.forms.models import inlineformset_factory
from django.utils import simplejson
from django.db import models
from django import forms


def node_form(request):
    class NodeForm(ModelForm):
        class Meta:
            model = Node 
        def __init__(self, *args, **kwargs):
            super(NodeForm, self).__init__(*args, **kwargs)
            for v in self.fields:
                self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'

    if request.method == 'POST':
        # return json: either errors or the redirect url
        form = NodeForm(request.POST)
        if form.is_valid():
            node = form.save()
            return HttpResponse(node.id)
    else: 
        form = NodeForm()
    return render_to_response('node_form.html', { 'form' : form }, context_instance=RequestContext(request))

def device_form(request):
    node_id = request.GET.get('node_id', None)
    try:
        node = Node.objects.get(id=node_id)
    except:
        return HttpResponseNotFound('No such node id')
    DeviceInlineFormSet = inlineformset_factory(Node, Device, extra=1)#, formfield_callback = my_formfield_cb)
    if request.method == "POST":
        formset = DeviceInlineFormSet(request.POST, instance=node, prefix='devices')
        if formset.is_valid():
            device_list = []
            #formset.save()
            for f in formset.forms:
                d = f.save()
                device_list.append(str(d.id))
            return HttpResponse( ','.join(device_list) )
    else:
        formset = DeviceInlineFormSet(instance=node, prefix='devices')
    return render_to_response("device_form.html", { "formset": formset })

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
    return render_to_response(template_form, { "formset": formset , 'device_id': device_id , 'configuration_type': entry_type , 'description': device.note } )

