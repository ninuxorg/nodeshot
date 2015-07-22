from rest_framework.serializers import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import Field
from netaddr import eui, ip


class MacAddressField(Field):
    """
    A field to handle mac address and avoid 500 internal server errors
    """
    def to_internal_value(self, value):
        try:
            return eui.EUI(value)
        except eui.AddrFormatError:
            raise ValidationError(_('Invalid mac address'))

    def to_representation(self, value):
        return str(value)


class IPAddressField(Field):
    """
    A field to handle ip address and avoid 500 internal server errors
    """
    def to_internal_value(self, value):
        try:
            return ip.IPAddress(value)
        except (ip.AddrFormatError, ValueError):
            raise ValidationError(_('Invalid ip address'))


    def to_representation(self, value):
        return str(value)


class IPNetworkField(Field):
    """
    A field to handle ip network and avoid 500 internal server errors
    """
    def to_internal_value(self, value):
        try:
            return ip.IPNetwork(value)
        except (ip.AddrFormatError, ValueError):
            raise ValidationError(_('Invalid ip network'))

    def to_representation(self, value):
        if value:
            return str(value)
        return value
