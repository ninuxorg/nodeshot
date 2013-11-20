"""
SSH base Connector Class
"""

__all__ = ['SSH']


import paramiko

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.utils import now
from nodeshot.networking.base.utils import ifconfig_to_dict
from nodeshot.networking.net.models import *
from nodeshot.networking.net.models.choices import DEVICE_STATUS

if 'nodeshot.networking.hardware' in settings.INSTALLED_APPS:
    HARDWARE_INSTALLED = True
    from nodeshot.networking.hardware.models import DeviceModel, Manufacturer, DeviceToModelRel
else:
    HARDWARE_INSTALLED = False


class SSH(object):
    """
    SSH base connector class
    """
    
    # costant
    REQUIRED_FIELDS = ['username', 'password']
    
    # SSH connection error message
    connection_error = None
    
    def __init__(self, device_connector):
        """
        store device_connector as an attribute
        """
        self.device_connector = device_connector
    
    def clean(self):
        """ validation method which will be called before saving the model in the django admin """
        self.check_required_fields()
        self.check_SSH_connection()
        self.ensure_no_duplicate()
        # close SSH connection
        self.close()
    
    def check_required_fields(self):
        """ check REQUIRED_FIELDS are filled """
        for field in self.REQUIRED_FIELDS:
            value = getattr(self.device_connector, field, None)
            
            if not value:
                raise ValidationError(_('%s is required for this connector class') % field)
    
    def check_SSH_connection(self):
        """ check SSH connection works """
        result = self.connect()
        
        if result is False:
            raise ValidationError(self.connection_error)
    
    def ensure_no_duplicate(self):
        """
        Ensure we're not creating a device that already exists
        Runs only when the DeviceConnector object is created, not when is updated
        """
        # if device_connector is being created right now
        if not self.device_connector.id:
            duplicates = []
            # loop over interfaces and check mac address
            for interface in self.get_interfaces():
                # shortcut for readability
                mac_address = interface['hardware_address']
                # avoid checking twice for the same interface (often ifconfig returns duplicates)
                if mac_address in duplicates:
                    continue
                # check in DB
                if Interface.objects.filter(mac__iexact=mac_address).count() > 0:
                    duplicates.append(mac_address)
            
            # if we have duplicates raise validation error
            if len(duplicates) > 0:
                # format list ['a', 'b', 'c'] as "a, b, c"
                mac_address_string = ', '.join(duplicates)
                raise ValidationError(_('interfaces with the following mac addresses already exist: %s') % mac_address_string)
    
    def connect(self):
        """
        Initialize SSH session
        
            returns True if success
            returns False and sets self.connection_error if something goes wrong
        """
        device_connector = self.device_connector
        
        shell = paramiko.SSHClient()
        shell.load_system_host_keys()
        shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            shell.connect(
                device_connector.host,
                username=device_connector.username,
                password=device_connector.password,
                port=device_connector.port
            )
            self.shell = shell
            # ok!
            return True
        # something went wrong
        except Exception as e:
            self.connection_error = e.message or e.strerror
            return False
    
    def exec_command(self, command, **kwargs):
        """ alias to paramiko.SSHClient.exec_command """
        return self.shell.exec_command(command, **kwargs)
    
    def output(self, command, **kwargs):
        """
        executes command and returns stdout if success or stderr if error
        """
        stdin, stdout, stderr = self.exec_command(command, **kwargs)
        
        output = stdout.read().strip()
        error = stderr.read().strip()
        
        # if error return error msg
        if error != '':
            return error
        # otherwise return output
        else:
            return output
    
    def close(self):
        """ closes SSH connection """
        self.shell.close()
    
    def start(self):
        """ start extracting info from device """
        # connect
        self.connect()
        
        # save device
        self.save_device()
        
        # get more info
        self.save_routing_protocols()
        self.save_interfaces()
        self.save_device_model()
        
        # close SSH connection
        self.close()
    
    def restart(self):
        """
        Delete db objects and start from scratch
        This method is used mainly for development purposes
        """
        # retrieve model indirectly because is needed only here
        DeviceConnector = self.device_connector.__class__
        
        # store original login info
        original_login = DeviceConnector(**{
            "node_id": self.device_connector.node_id,
            "host": self.device_connector.host,
            "username": self.device_connector.username,
            "password": self.device_connector.password,
            "store": True,
            "port": self.device_connector.port,
            "connector_class": self.device_connector.connector_class
        })
        # delete device
        self.device_connector.device.delete()
        
        # save login and restart
        original_login.save()
    
    def save_device(self):
        """ save Device object """
        device = Device()
        device.node = self.device_connector.node
        device.name = self.get_device_name()
        # get_os() returns a tuple
        device.os, device.os_version = self.get_os()
        # we are pretty sure the device is a radio device :)
        device.type = 'radio'
        # we are pretty sure the device is reachable too!
        device.status = DEVICE_STATUS.get('reachable')
        # this is the first time the device is seen by the system because we are just adding it
        device.first_seen = now()
        # and is also the latest
        device.last_seen = now()
        device.save()
        
        self.device = device
    
    def save_routing_protocols(self):
        """ save routing protocols info """
        self.check_olsr()
    
    def save_interfaces(self):
        """
        save interfaces and relative ip addresses
        """
        interfaces = self.get_interfaces()
        device = self.device
        
        for interface in interfaces:
            # if this is an interesting interface
            if interface['ip_address'] != '':
                obj = None
                
                # is it Ethernet?
                if 'eth' in interface['interface']:
                    
                    standard = self.get_ethernet_standard()
                    duplex = self.get_ethernet_duplex()
                    
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
                    
                    wireless_mode = self.get_wireless_mode()
                    wireless_channel = self.get_wireless_channel()
                    wireless_channel_width = self.get_wireless_channel_width()
                    wireless_output_power = self.get_wireless_output_power()
                    wireless_dbm = self.get_wireless_dbm()
                    wireless_noise = self.get_wireless_noise()
                    
                    # initialize ethernet interface
                    obj = Wireless(**{
                        'device': device,
                        'name': interface['interface'],
                        'mac': interface['hardware_address'],
                        'mode': wireless_mode,
                        'standard': '802.11n',
                        'channel': wireless_channel,
                        'channel_width': wireless_channel_width,
                        'output_power': wireless_output_power,
                        'dbm': wireless_dbm,
                        'noise': wireless_noise,
                    })
                    # save into DB
                    obj.save()
                else:
                    # TODO!!! VPN, BRIDGES, VLANS, etc..
                    pass
                
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
    
    def get_interfaces(self):
        """ get device interfaces """
        return ifconfig_to_dict(self.output('ifconfig'))
    
    def get_ipv6_of_interface(self, interface_name):
        """ return ipv6 address for specified interface """
        command = "ip -6 addr show %s" % interface_name
        
        output = self.output(command)
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'global' in line:
                parts = line.split(' ')
                ipv6 = parts[1]
                break
        
        return ipv6
    
    def check_olsr(self):
        """
        check if olsr is installed, if yes will add this info
        """
        version_string = self.output('olsrd -v')
        
        if 'not found' in version_string:
            # exit here
            return False
        
        # extract olsr version and url
        lines = version_string.split('\n')
        version = lines[0].split(' - ')[1].strip()
        url = lines[2].strip()
    
        # ensure RoutingProtocol object is in DB
        try:
            olsr = RoutingProtocol.objects.filter(
                name__icontains='olsr',
                version__icontains=version,
                url__icontains=url
            )[0]
        # otherwise create it
        except IndexError:
            olsr = RoutingProtocol(name='OLSR', version=version, url=url)
            olsr.save()
        
        self.device.routing_protocols.add(olsr)
        
        return True
    
    def save_device_model(self):
        """
        If nodeshot.networking.hardware module is installed
        Get device model info and store in DB
        """
        if HARDWARE_INSTALLED:
            # try getting device model from db
            try:
                device_model = DeviceModel.objects.filter(name=self.get_device_model())[0]
            # if it does not exist create it
            except IndexError as e:
                try:
                    manufacturer = Manufacturer.objects.filter(name__icontains='ubiquiti')[0]
                    device_model = DeviceModel(
                        manufacturer=manufacturer,
                        name=self.get_device_model()
                    )
                    device_model.ram = self.get_device_RAM()
                except IndexError as e:
                    device_model = False
            
            # create relation between device model and device
            if device_model:
                device_model.save()
                rel = DeviceToModelRel(device=self.device, model=device_model)
                rel.save()
    
    def get_os(self):
        """
        should return a tuple in which
            the first element is the OS name and
            the second element is the OS version
        """
        raise NotImplementedError('get_os method must be overridden')
    
    def get_device_name(self):
        raise NotImplementedError('get_device_name method must be overridden')
    
    def get_device_model(self):
        raise NotImplementedError('get_device_model method must be overridden')
    
    def get_device_RAM(self):
        raise NotImplementedError('get_device_RAM method must be overridden')
    
    def get_ethernet_standard(self):
        raise NotImplementedError('get_ethernet_standard method must be overridden')
    
    def get_ethernet_duplex(self):
        raise NotImplementedError('get_ethernet_duplex method must be overridden')
    
    def get_wireless_channel_width(self):
        raise NotImplementedError('get_wireless_channel_width method must be overridden')
    
    def get_wireless_mode(self):
        raise NotImplementedError('get_wireless_mode method must be overridden')
    
    def get_wireless_channel(self):
        raise NotImplementedError('get_wireless_channel method must be overridden')
    
    def get_wireless_output_power(self):
        raise NotImplementedError('get_wireless_output_power method must be overridden')
    
    def get_wireless_dbm(self):
        raise NotImplementedError('get_wireless_dbm method must be overridden')
    
    def get_wireless_noise(self):
        raise NotImplementedError('get_wireless_noise method must be overridden')
