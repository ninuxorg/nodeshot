from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import WritableField
from netaddr import eui, ip


class MacAddressField(WritableField):
        """
        A field to handle mac address and avoid 500 internal server errors
        """
        
        def validate(self, value):
            """ ensure valid mac """
            super(MacAddressField, self).validate(value)
            
            try:
                eui.EUI(value)
            except eui.AddrFormatError:
                raise ValidationError(_('Invalid mac address'))
        
        def from_native(self, value):
            return value
    
        def to_native(self, value):
            return unicode(value)


class IPAddressField(WritableField):
        """
        A field to handle ip address and avoid 500 internal server errors
        """
        
        def validate(self, value):
            """ ensure valid ip address """
            super(IPAddressField, self).validate(value)
            
            try:
                ip.IPAddress(value)
            except (ip.AddrFormatError, ValueError):
                raise ValidationError(_('Invalid ip address'))
        
        def from_native(self, value):
            return value
    
        def to_native(self, value):
            return unicode(value)


class IPNetworkField(WritableField):
        """
        A field to handle ip network and avoid 500 internal server errors
        """
        
        def validate(self, value):
            """ ensure valid ip network """
            super(IPNetworkField, self).validate(value)
            
            try:
                ip.IPNetwork(value)
            except (ip.AddrFormatError, ValueError):
                raise ValidationError(_('Invalid ip network'))
        
        def from_native(self, value):
            return value
    
        def to_native(self, value):
            if value:
                return unicode(value)
            return value