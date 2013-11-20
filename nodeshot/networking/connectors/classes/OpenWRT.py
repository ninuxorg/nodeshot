"""
Class to extract information from  OpenWRT devices
"""

__all__ = ['OpenWRT']


from .ssh import SSH


class OpenWRT(SSH):
    """
    OpenWRT SSH connector
    """
       
    def get_device_name(self):
        """ get device name """
        return self.output('uname -a').split(' ')[1]
    
    def get_os(self):
        """ get os name and version, return as tuple """
        # cache command output
        output = self.output('cat /etc/openwrt_release')
        
        # init empty dict
        info = {}
        
        # loop over lines of output
        # parse output and store in python dict
        for line in output.split('\n'):
            # tidy up before filling the dictionary
            key, value = line.split('=')
            key = key.replace('DISTRIB_', '').lower()
            value = value.replace('"', '')
            # fill!
            info[key] = value
        
        os = info['id']
        version = info['release']
        
        if info['description']:
            
            if info['revision']:
                additional_info = "%(description)s, %(revision)s" % info
            else:
                additional_info = "%(description)s" % info
            
            # remove redundant OpenWRT occuerrence
            additional_info = additional_info.replace('OpenWrt ', '')
            
            version = "%s (%s)" % (version, additional_info)
       
        return (os, version)
    
    def save_device_model(self):
        pass
    
    def get_device_model(self):
        """ get device model name, eg: Nanostation M5, Rocket M5 """
        output = output = self.output('iwinfo | grep -i hardware')
        # will return something like
        # Hardware: 168C:002A 0777:E805 [Ubiquiti Bullet M5]
        # and we'll extract only the string between square brackets
        return output.split('[')[1].replace(']','')
    
    # TODO follows
    
    def get_device_RAM(self):
        return 0
    
    def get_ethernet_standard(self):
        """ determine ethernet standard """
        return 'fast'
    
    def get_ethernet_duplex(self):
        """ determine if ethernet interface is full-duplex or not """
        return 'duplex'
    
    def get_wireless_mode(self):
        """ retrieve wireless mode (AP/STA) """
        return 'ap'
    
    def get_wireless_channel(self):
        """ retrieve wireless channel / frequency """
        return '2412'
    
    def get_wireless_channel_width(self):
        """ retrieve wireless channel width """
        return '20'
    
    def get_wireless_output_power(self):
        """ retrieve output power """
        return None
    
    def get_wireless_dbm(self):
        """ get dbm """
        return None
    
    def get_wireless_noise(self):
        """ retrieve noise """
        return None