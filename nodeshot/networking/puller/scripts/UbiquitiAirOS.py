"""
Class to extract information from Ubiquiti AirOS devices
"""

__all__ = ['UbiquitiAirOS']


import spur

from django.conf import settings

from nodeshot.networking.base.utils import ifconfig_to_dict
from nodeshot.networking.net.models import *
from nodeshot.networking.net.models.choices import DEVICE_STATUS, DEVICE_TYPES

if 'nodeshot.networking.hardware' in settings.INSTALLED_APPS:
    HARDWARE_INSTALLED = True
    from nodeshot.networking.hardware.models import DeviceModel, Manufacturer, DeviceToModelRel
else:
    HARDWARE_INSTALLED = False

class UbiquitiAirOS(object):
    """
    Ubiquiti AirOS SSH puller
    """
    
    def __init__(self, device_login):
        self.shell = spur.SshShell(**{
            'hostname': device_login.host,
            'username': device_login.username,
            'password': device_login.password,
            'port': device_login.port
        })
        self.device_login = device_login
    
    def restart(self):
        """ delete db objects and start from scratch """
        # retrieve model indirectly because is needed only here
        DeviceLogin = self.device_login.__class__
        # store original login info
        original_login = DeviceLogin(**{
            "node_id": self.device_login.node_id,
            "host": self.device_login.host,
            "username": self.device_login.username,
            "password": self.device_login.password,
            "store": True,
            "port": self.device_login.port,
            "puller_class": self.device_login.puller_class
        })
        # delete device
        self.device_login.device.delete()
        # save login and restart
        original_login.save()
    
    def start(self):
        """ start extracting info from device """
        self.ubntbox = self.get_ubntbox()
        self.systemcfg = self.get_systemcfg()
        
        device = Device()
        device.node = self.device_login.node
        device.name = self.get_device_name()
        device.firmware = self.ubntbox['firmwareVersion']
        device.os = self.get_os()
        device.type = 'radio'
        device.status = DEVICE_STATUS.get('reachable')
        device.save()
        
        if HARDWARE_INSTALLED:
            # try getting device model from db
            try:
                device_model = DeviceModel.objects.filter(name=self.ubntbox['platform'])[0]
            except IndexError as e:
                try:
                    manufacturer = Manufacturer.objects.filter(name__icontains='ubiquiti')[0]
                    device_model = DeviceModel(
                        manufacturer=manufacturer,
                        name=self.ubntbox['platform']
                    )
                    device_model.ram = self.ubntbox['memTotal']
                except IndexError as e:
                    device_model = False
            
            if device_model:
                device_model.save()
                rel = DeviceToModelRel(device=device, model=device_model)
                rel.save()
        
        self.check_if_olsr_and_which_version(device)
        self.device = device
        
        self.save_interfaces(device)
        
        #self.self.ubntbox['platform']
    
    def run(self, command, **kwargs):
        return self.shell.run(command.split(' '), **kwargs)
    
    def output(self, command, **kwargs):
        try:
            return self.run(command, **kwargs).output.strip()
        except spur.RunProcessError as e:
            return e.output.strip()
    
    def get_os(self):
        return self.output('cat /proc/version').split('#')[0]
    
    def get_device_name(self):
        return self.output('uname -a').split(' ')[1]
    
    def check_if_olsr_and_which_version(self, device):
        try:
            self.output('which olsrd')
            version_string = self.output('olsrd -v')
        except spur.RunProcessError:
            return 
        
        # extract olsr version and url
        lines = version_string.split('\n')
        version = lines[0].split(' - ')[1].strip()
        url = lines[2].strip()
    
        try:
            olsr = RoutingProtocol.objects.filter(
                name__icontains='olsr',
                version__icontains=version,
                url__icontains=url
            )[0]
        except IndexError:
            olsr = RoutingProtocol(name='OLSR', version=version, url=url)
            olsr.save()
        device.routing_protocols.add(olsr)
    
    def get_ubntbox(self):
        """
        ubntbox mca-status
        """
        output = self.output('ubntbox mca-status')
        
        info = {}
        
        for line in output.split('\r\n'):
            parts = line.split('=')
            
            # main device info
            if len(parts) > 2:
                subparts = line.split(',')
                for subpart in subparts:
                    key, value = subpart.split('=')
                    info[key] = value
            # all other stuff
            elif len(parts) == 2:
                info[parts[0]] = parts[1]
            else:
                pass
        
        return info
    
    def get_systemcfg(self):
        """ get main system configuration """
        output = self.output('cat /tmp/system.cfg')
        
        info = {}
        
        for line in output.split('\n'):
            parts = line.split('=')
            
            if len(parts) == 2:
                info[parts[0]] = parts[1]
        
        return info
    
    def get_ipv6_of_interface(self, interface_name):
        """ return ipv6 address for specified interface """
        command = "ip -6 addr show %s" % interface_name
        
        try:
            output = self.output(command)
        except spur.RunProcessError:
            return None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'global' in line:
                parts = line.split(' ')
                ipv6 = parts[1]
                break
        
        return ipv6
        
    def get_interfaces(self):
        """ get device interfaces """
        return ifconfig_to_dict(self.output('ifconfig'))
    
    def save_interfaces(self, device):
        interfaces = self.get_interfaces()
        
        for interface in interfaces:
            # if this is an interesting interface
            if interface['ip_address'] != '':
                obj = None
                
                # is it Ethernet?
                if 'eth' in interface['interface']:
                    # determine ethernet standard
                    if '100Mbps' in self.ubntbox['lanSpeed']:
                        standard = 'fast'
                    elif '1000Mbps' in self.ubntbox['lanSpeed']:
                        standard = 'gigabit'
                    elif '10Mbps' in self.ubntbox['lanSpeed']:
                        standard = 'legacy'
                    
                    # determine ethernet standard
                    if 'Full' in self.ubntbox['lanSpeed']:
                        duplex = 'full'
                    elif 'Half' in self.ubntbox['lanSpeed']:
                        duplex = 'half'
                    
                    # initialize ethernet interface
                    obj = Ethernet(**{
                        'device': device,
                        'name': interface['interface'],
                        'mac': interface['hardware_address'],
                        'standard': standard,
                        'duplex': duplex,
                    })
                    # save into DB
                    obj.save()
                # is it Wireless?
                elif 'wlan' in interface['interface'] or 'ath' in interface['interface']:
                    if '20' in self.systemcfg['radio.1.ieee_mode']:
                        channel_width = 20
                    elif '40' in self.systemcfg['radio.1.ieee_mode']:
                        channel_width = 40
                    else:
                        channel_width = None
                    # initialize ethernet interface
                    obj = Wireless(**{
                        'device': device,
                        'name': interface['interface'],
                        'mac': interface['hardware_address'],
                        'mode': self.ubntbox['wlanOpmode'],
                        'standard': '802.11n',
                        'channel': self.ubntbox['freq'],
                        'channel_width': channel_width,
                        'output_power': int(self.systemcfg['radio.1.txpower']),
                        'dbm': self.ubntbox['signal'],
                        'noise': self.ubntbox['noise'],
                    })
                    # save into DB
                    obj.save()
                    
                    
                
                # save ipv4 address if necessary
                if obj:
                    Ip.objects.create(**{
                        'interface': obj,
                        'address': interface['ip_address'],
                    })
                
                # save ipv6 address if any
                ipv6_address = self.get_ipv6_of_interface(interface['interface'])
                if ipv6_address:
                    # subtract netmask
                    ipv6_address = ipv6_address.split('/')[0]
                    Ip.objects.create(**{
                        'interface': obj,
                        'address': ipv6_address,
                    })