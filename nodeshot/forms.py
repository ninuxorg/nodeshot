from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from nodeshot.models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import *
from django.forms.models import inlineformset_factory
from django.utils import simplejson
from django.db import models
from django import forms
from settings import DEBUG
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

# base NodeForm class
class BaseNodeForm(forms.ModelForm):
    ''' Base Form Node, other forms will extend this class '''
    
    class Meta:
        model = Node
    
    def __init__(self, *args, **kwargs):
        super(BaseNodeForm, self).__init__(*args, **kwargs)
        # css classes for fields
        for v in self.fields:
            self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'

    def clean(self):
        ''' Calls parent clean() and performs additional validation for the password field '''
        super(BaseNodeForm, self).clean()
        
        # strip() values
        for field in self.cleaned_data: 
            if isinstance(self.cleaned_data[field], basestring): 
                self.cleaned_data[field] = self.cleaned_data[field].strip() 
        
        return self.cleaned_data

class AddNodeForm(BaseNodeForm):
    ''' Form to add a node, has an additional password2 field for password verification '''
    
    password2 = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput())

    def clean(self):
        ''' Calls parent clean() and performs additional validation for the password field '''
        super(NodeForm, self).clean()
        
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        # password and password2 must be the same
        if password != password2:
            raise forms.ValidationError('I due campi password non corrispondono.')
        else:
            return self.cleaned_data

class EditNodeForm(BaseNodeForm):
    ''' Form to edit a node '''
    
    class Meta:
        model = Node
        exclude = ('status', 'password', 'slug')

def node_form(request):
    ''' View for add/edit node '''

    # retrieve node ID
    node_id = request.GET.get('id', None)

    # if form has been submitted
    if request.method == 'POST':
        # if a new node has been submitted
        if node_id == None:
            # return json: either errors or the redirect url
            form = AddNodeForm(request.POST)
            # if form is valid
            if form.is_valid():
                # prepare the node model object but don't save in the database yet
                node = form.save(commit=False)
                # set node as unconfirmed for security reasons, infact malicious users could edit the hidden field easily with instruments like firebug.
                node.status = 'u'
                # make slug
                node.slug = slugify(node.name)
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
            form = AddNodeForm(request.POST, instance=node)
            # if form is valid
            if form.is_valid():
                # save in the database
                form.save()
            
    # if form hasn't been submitted and we are going to edit an existing node
    elif request.method != 'POST' and node_id != None:
        # get object or return a 404
        node = get_object_or_404(Node, pk=node_id)
        # populate the form with the current node info
        form = AddNodeForm(instance=node)
    # if inserting a new node
    else:
        # blank form
        form = AddNodeForm()
    
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
    
def edit_node(request, node_id):
        
    # if request is sent with ajax
    if request.is_ajax():
        template = 'ajax/edit_node.html';
    else:
        # alternative mode available just for testing
        if DEBUG:
            template = 'edit_node.html';
        else:
            raise Http404
        
    # get object or raise 404
    try:
        node = Node.objects.select_related().get(pk=node_id)
    except DoesNotExists:
        raise Http404
    # if node is unconfirmed return 404 error
    if node.status == 'u':
        raise Http404
    
    # raw password to authenticate
    raw_password = request.POST.get('raw_password', False)
    # once authenticated password is sent in ecrypted format
    encrypted_password = request.POST.get('encrypted_password', False)
    # default value for authenticated variable
    authenticated = 0
    # init form
    form = EditNodeForm(instance=node)
    # default value for save variable
    saved = False
    
    # if sending raw password check if is correct
    if raw_password and node.check_password(raw_password):
        authenticated = 1
        encrypted_password = node.password
    # if password is not correct value of authenticated is 2
    elif raw_password and not node.check_password(raw_password):
        authenticated = 2
    # if password is being sent in encrypted format it means we are editing the form
    elif encrypted_password and encrypted_password == node.password:
        authenticated = 1
        # init edit form with POST values
        form = EditNodeForm(request.POST, instance=node)
        
        if form.is_valid():
            node = form.save(commit=False)
            node.slug = slugify(node.name)
            node.save()
            # this tells the template that the form has saved in order to display a message to the user
            saved = True
    
    context = {
        'node': node,
        'form' : form,
        'authenticated': authenticated,
        'encrypted_password': encrypted_password,
        'saved': saved
    }
    
    return render_to_response(template, context, context_instance=RequestContext(request))

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

class PasswordRecoveryForm(forms.Form):
    """
    A form used to recover the password of a node.
    """
    
    email = forms.EmailField(min_length=8, max_length=100)
    
    def __init__(self, node, *args, **kwargs):
        self.node = node
        super(PasswordRecoveryForm, self).__init__(*args, **kwargs)
        # css classes for fields
        for v in self.fields:
            self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'
            
    def clean_email(self):
        ''' check if email corresponds to one of the node owners '''
        
        email = self.cleaned_data['email']
        node = self.node
        
        import logging
        logging.log(1, self.cleaned_data)
        
        if email != node.email and email != node.email2 and email != node.email3:
            raise forms.ValidationError('L\'email inserita non corrisponde a nessuna delle email dei responsabili del nodo.')
        
        return email

class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a node in the admin interface.
    """
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def __init__(self, node, *args, **kwargs):
        self.node = node
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.node.password = self.cleaned_data["password1"]
        self.node.set_password()
        if commit:
            self.node.save()
        return self.node
    
from math_captcha import MathCaptchaModelForm

class ContactForm(MathCaptchaModelForm):
    """
    A form used to contact node owners
    """
    
    class Meta:
        model = Contact
    
    from_name = forms.CharField(max_length=50, min_length=4, widget=forms.TextInput)
    from_email = forms.EmailField(max_length=50, min_length=8, widget=forms.TextInput)
    message = forms.CharField(max_length=2000, widget=forms.Textarea)
    # extra antispam
    honeypot = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    
    def __init__(self, extra=False, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        # if extra values are being passed
        if extra:
            # create a new editable QueryDict object (only copied QueryDict objects are editable)
            new_data = self.data.copy()
            # fill the new QueryDict object with extra values
            new_data['node'] = extra.get('node')
            new_data['ip'] = extra.get('ip')
            new_data['user_agent'] = extra.get('user_agent')
            new_data['accept_language'] = extra.get('accept_language')
            # substitute old QueryDict object with new one
            self.data = new_data
        # css classes for fields
        for v in self.fields:
            self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'
    
    def clean(self):
        ''' Strip values '''
        super(ContactForm, self).clean()
        
        # strip() values
        for field in self.cleaned_data: 
            if isinstance(self.cleaned_data[field], basestring): 
                self.cleaned_data[field] = self.cleaned_data[field].strip()
        
        # if honeypot is True it surely means a spambot or something like that is trying to submit the form.
        if self.cleaned_data.get('honeypot', False)==True:
            # return a silly error
            raise forms.ValidationError(_("Error 500"))
        
        return self.cleaned_data