import sys
import re
import json

# ------- IFCONFIG TO JSON CONVERSION ------- #
# credits:
# https://gist.github.com/snbartell/1586034

def _extract(ifconfig_output):
    mo = re.search(r'^(?P<interface>\w+|\w+:\d+)\s+' +
                     r'Link encap:(?P<link_encap>\S+)\s+' +
                     r'(HWaddr\s+(?P<hardware_address>\S+))?' +
                     r'(\s+inet addr:(?P<ip_address>\S+))?' +
                     r'(\s+inet6 addr:(?P<ipv6_address>\S+)Scope:Global)?' +
                     r'(\s+Bcast:(?P<broadcast_address>\S+)\s+)?' +
                     r'(Mask:(?P<net_mask>\S+)\s+)?',
                     ifconfig_output, re.MULTILINE|re.IGNORECASE )
    if mo:
        info = mo.groupdict('')
        info['running'] = False
        info['up'] = False
        info['multicast'] = False
        info['broadcast'] = False
        if 'RUNNING' in ifconfig_output:
            info['running'] = True
        if 'UP' in ifconfig_output:
            info['up'] = True
        if 'BROADCAST' in ifconfig_output:
            info['broadcast'] = True
        if 'MULTICAST' in ifconfig_output:
            info['multicast'] = True
        return info
    return {}
 

def ifconfig_to_dict(ifconfig):
    interfaces = [ _extract(interface) for interface in ifconfig.split('\n\n') if interface.strip() ]
    return interfaces

def ifconfig_to_json(ifconfig, indent=4):
    interfaces = ifconfig_to_dict(ifconfig)
    return json.dumps(interfaces, indent=indent)