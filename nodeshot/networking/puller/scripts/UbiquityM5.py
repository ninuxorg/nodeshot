"""
Classes to extract information from Ubiquity Devices
"""

__all__ = ['UbiquityM5']


import spur

from nodeshot.networking.net.models import *
from nodeshot.networking.net.models.choices import DEVICE_STATUS, DEVICE_TYPES


class UbiquityM5(object):
    """
    Ubiquity M5 series
    """
    
    def __init__(self, device_login):
        self.shell = spur.SshShell(**{
            'hostname': device_login.host,
            'username': device_login.username,
            'password': device_login.password,
            'port': device_login.port
        })
        self.device_login = device_login
    
    def start(self):
        self.device = Device()
        self.device.node = self.device_login.node
        self.device.name = self.get_device_name()
        self.device.os = self.get_os()
        self.device.type = 'radio'
        self.device.status = DEVICE_STATUS.get('reachable')
        self.device.save()
        if self.has_olsr():
            try:
                olsr = RoutingProtocol.objects.filter(name__icontains='olsr')[0]
            except RoutingProtocol.DoesNotExist:
                olsr = RoutingProtocol(name='olsr')
                olsr.save()
            self.device.routing_protocols.add(olsr)
    
    def run(self, command, **kwargs):
        return self.shell.run(command.split(' '), **kwargs)
    
    def output(self, command, **kwargs):
        return self.run(command, **kwargs).output.strip()
    
    def get_os(self):
        return self.output('cat /proc/version').split('#')[0]
    
    def get_device_name(self):
        return self.output('uname -a').split(' ')[1]
    
    def has_olsr(self):
        try:
            return 'No such file' not in self.output('find olsrd.conf', cwd='/')
        except spur.RunProcessError:
            pass
        return False
