"""
Class to extract information from Ubiquiti AirOS devices
"""

__all__ = ['UbiquitiAirOS']


from .ssh import SSH


class UbiquitiAirOS(SSH):
    """
    Ubiquiti AirOS SSH connector
    """
    
    _ubntbox = None
    _systemcfg = None
    
    @property
    def ubntbox(self):
        """
        returns ubntbox mca-status output
        """
        # get result if not present in memory yet
        if not self._ubntbox:
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
        
            self._ubntbox = info
        
        # return output
        return self._ubntbox
    
    @property
    def systemcfg(self):
        """
        return main system configuration
        """
        # if config hasn't been retrieved yet do it now
        if not self._systemcfg:
            output = self.output('cat /tmp/system.cfg')
        
            info = {}
            
            for line in output.split('\n'):
                parts = line.split('=')
                
                if len(parts) == 2:
                    info[parts[0]] = parts[1]
            
            self._systemcfg = info
        
        # return config
        return self._systemcfg
    
    def get_os(self):
        """ get OS string """
        return self.output('cat /proc/version').split('#')[0]
    
    def get_device_name(self):
        """ get device name """
        return self.output('uname -a').split(' ')[1]
    
    def get_firmware(self):
        """ get firmware name and version """
        return self.ubntbox['firmwareVersion']
    
    def get_device_model(self):
        """ get device model name, eg: Nanostation M5, Rocket M5 """
        return self.ubntbox['platform']
    
    def get_device_RAM(self):
        return self.ubntbox['memTotal']
    
    def get_ethernet_standard(self):
        """ determine ethernet standard """
        if '100Mbps' in self.ubntbox['lanSpeed']:
            return 'fast'
        elif '1000Mbps' in self.ubntbox['lanSpeed']:
            return 'gigabit'
        elif '10Mbps' in self.ubntbox['lanSpeed']:
            return 'legacy'
        else:
            return None
    
    def get_ethernet_duplex(self):
        """ determine if ethernet interface is full-duplex or not """
        if 'Full' in self.ubntbox['lanSpeed']:
            return 'full'
        elif 'Half' in self.ubntbox['lanSpeed']:
            return 'half'
    
    def get_wireless_channel_width(self):
        """ retrieve wireless channel width """
        if '20' in self.systemcfg['radio.1.ieee_mode']:
            return 20
        elif '40' in self.systemcfg['radio.1.ieee_mode']:
            return 40
        else:
            return None
    
    def get_wireless_mode(self):
        """ retrieve wireless mode (AP/STA) """
        return self.ubntbox['wlanOpmode']
    
    def get_wireless_channel(self):
        """ retrieve wireless channel / frequency """
        return self.ubntbox['freq']
    
    def get_wireless_output_power(self):
        """ retrieve output power """
        return int(self.systemcfg['radio.1.txpower'])
    
    def get_wireless_dbm(self):
        """ get dbm """
        return self.ubntbox['signal']
    
    def get_wireless_noise(self):
        """ retrieve noise """
        return self.ubntbox['noise']