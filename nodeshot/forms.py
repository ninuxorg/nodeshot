from nodeshot.models import *
from django.conf import settings
from django.forms.models import inlineformset_factory
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseInlineFormSet
from settings import DEBUG

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
    '''
    Add node django form
    has an additional password2 field for password verification
    '''
    
    password2 = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput())

    def clean(self):
        ''' Calls parent clean() and performs additional validation for the password field '''
        super(AddNodeForm, self).clean()
        
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        # password and password2 must be the same
        if password != password2:
            raise forms.ValidationError(_('The two password fields didn\'t match.'))
        else:
            return self.cleaned_data

class EditNodeForm(BaseNodeForm):
    '''
    Edit node django form
    if new_password and new_password2 fields are filled the view will take care of updating the password
    '''
    
    new_password = forms.CharField(max_length=20, required=False, widget=forms.PasswordInput())
    new_password2 = forms.CharField(max_length=20, required=False, widget=forms.PasswordInput())

    def clean(self):
        ''' Calls parent clean() and performs additional validation for the password field '''
        super(EditNodeForm, self).clean()
        
        new_password = self.cleaned_data.get('new_password')
        new_password2 = self.cleaned_data.get('new_password2')

        # password and password2 must be the same
        if new_password != new_password2:
            raise forms.ValidationError(_('The two password fields didn\'t match.'))
        else:
            return self.cleaned_data
    
    class Meta:
        model = Node
        exclude = ('status', 'slug', 'password')

class PasswordResetForm(forms.Form):
    """
    A form used to recover the password of a node.
    """
    
    email = forms.EmailField(min_length=8, max_length=100)
    
    def __init__(self, node, *args, **kwargs):
        self.node = node
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        # css classes for fields
        for v in self.fields:
            self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'
            
    def clean_email(self):
        ''' check if email corresponds to one of the node owners '''
        
        email = self.cleaned_data['email'].lower()
        node = self.node
        
        # check email submitted is one of the node owners, the check is case insensitive
        try:
            if email != node.email.lower() and email != node.email2.lower() and email != node.email3.lower():
                raise forms.ValidationError(_("The inserted email doesn't match any of the node owners' emails"))
        # this is for the cases in which email2 or email3 fields are NULL (eg: in the case the database was imported)
        except:
            if email != node.email.lower() and email != node.email2 and email != node.email3: #
                raise forms.ValidationError(_("The inserted email doesn't match any of the node owners' emails"))
        
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

# admin
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device

    def clean_cname(self):
        """
        Empty cname defaults to slugify(name)
        """
        cname = self.cleaned_data.get('cname', False)
        name = self.cleaned_data.get('name', False)
        if not cname or cname == '':
            cname = slugify(name)
        return cname
    
# frontend
class DeviceInlineFormset(BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            def clean_cname(self):
                """
                This does not really work and I can't understand the reason.
                The default value for cname is set by the model's overwritten save() method.
                This is necessary to avoid the validation error about the field not being unique if CNAME left empty
                by Nemesis
                """
                cname = self.cleaned_data.get('cname', False)
                name = self.cleaned_data.get('name', False)
                if not cname or cname == '':
                    cname = slugify(name)
                return cname

# admin
class InterfaceForm(forms.ModelForm):
    class Meta:
        model = Interface
        
    def clean_cname(self):
        """
        Empty cname defaults to interface type
        """
        cname = self.cleaned_data.get('cname', False)
        if not cname or cname == '':
            cname = self.cleaned_data.get('type')
        return cname

    def clean_ipv4_address(self):
        """
        Return None instead of empty string
        """
        return self.cleaned_data.get('ipv4_address') or None
    
    def clean_ipv6_address(self):
        """
        Return None instead of empty string
        """
        return self.cleaned_data.get('ipv6_address') or None
        
    def clean_mac_address(self):
        """
        Return None instead of empty string
        """
        return self.cleaned_data.get('mac_address') or None

# frontend
class InterfaceInlineFormset(BaseInlineFormSet):    
    def clean(self):
        for form in self.forms:
                
            def clean_ipv4_address(self):
                """
                Return None instead of empty string
                """
                return self.cleaned_data.get('ipv4_address') or None
            
            def clean_ipv6_address(self):
                """
                Return None instead of empty string
                """
                return self.cleaned_data.get('ipv6_address') or None
                
            def clean_mac_address(self):
                """
                Return None instead of empty string
                """
                return self.cleaned_data.get('mac_address') or None
    
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
            self.fields[v].widget.attrs['class'] = 'text'
    
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