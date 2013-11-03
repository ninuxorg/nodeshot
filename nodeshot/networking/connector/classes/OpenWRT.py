"""
Class to extract information from  OpenWRT devices
"""

__all__ = ['OpenWRT']


from .ssh import SSH


class OpenWRT(SSH):
    """
    OpenWRT SSH connector
    """
    
    def get_os(self):
        """ get OS string """
        return self.output('cat /proc/version').split('#')[0]
    
    def get_device_name(self):
        """ get device name """
        return self.output('uname -a').split(' ')[1]
    
    def get_firmware(self):
        """ get firmware name and version """
        # cache command output
        output = self.output('cat /etc/openwrt_release')
        
        # init empty dict
        release = {}
        
        # loop over lines of output
        # parse output and store in python dict
        for line in output.split('\n'):
            # tidy up before filling the dictionary
            key, value = line.split('=')
            key = key.replace('DISTRIB_', '').lower()
            value = value.replace('"', '')
            # fill!
            release[key] = value
        
        main_name = "%(id)s %(release)s" % release
        
        if release['description']:
            
            if release['revision']:
                additional_info = "%(description)s, %(revision)s" % release
            else:
                additional_info = "%(description)s" % release
            
            # remove redundant OpenWRT occuerrence
            additional_info = additional_info.replace('OpenWrt ', '')
            
            result = "%s (%s)" % (main_name, additional_info)
       
        return result
    
    def get_device_model(self):
        """ get device model name, eg: Nanostation M5, Rocket M5 """
        output = output = self.output('iwinfo | grep -i hardware')
        # will return something like
        # Hardware: 168C:002A 0777:E805 [Ubiquiti Bullet M5]
        # and we'll extract only the string between square brackets
        return output.split('[')[1].replace(']','')
    
    def get_device_RAM(self):
        return ''
    
    def get_ethernet_standard(self):
        """ determine ethernet standard """
        return ''
    
    def get_ethernet_duplex(self):
        """ determine if ethernet interface is full-duplex or not """
        return ''
    
    def get_wireless_mode(self):
        """ retrieve wireless mode (AP/STA) """
        return ''
    
    def get_wireless_channel(self):
        """ retrieve wireless channel / frequency """
        return ''
    
    def get_wireless_channel_width(self):
        """ retrieve wireless channel width """
        return ''
    
    def get_wireless_output_power(self):
        """ retrieve output power """
        return ''
    
    def get_wireless_dbm(self):
        """ get dbm """
        return ''
    
    def get_wireless_noise(self):
        """ retrieve noise """
        return ''