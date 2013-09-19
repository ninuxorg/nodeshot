"""
Classes to extract information from Ubiquity Devices
"""

__all__ = ['UbiquityM5']


import spur

from nodeshot.networking.base.utils import ifconfig_to_dict
from nodeshot.networking.net.models import *
from nodeshot.networking.net.models.choices import DEVICE_STATUS, DEVICE_TYPES


class UbiquityM5AirOS(object):
    """
    Ubiquity M5 series mounting AirOS
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
        original_login = self.device_login
        self.device_login.device.delete()
        original_login.id = None
        original_login.save()
        self.start()
    
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
        self.check_if_olsr_and_which_version(device)
        self.device = device
        
        self.save_interfaces(device)
    
    def run(self, command, **kwargs):
        return self.shell.run(command.split(' '), **kwargs)
    
    def output(self, command, **kwargs):
        return self.run(command, **kwargs).output.strip()
    
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
                
                # save ip address if necessary
                if obj:
                    Ip.objects.create(**{
                        'interface': obj,
                        'address': interface['ip_address'],
                    })
                