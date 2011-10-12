#!/usr/bin/env python

from pysnmp.entity.rfc3413.oneliner import cmdgen
import sys, os, struct, threading

# determine directory automatically
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.abspath(os.path.join(directory, os.path.pardir, os.path.pardir))
sys.path.append(parent)

from django.core.management import setup_environ
import settings
setup_environ(settings)
__builtins__.IS_SCRIPT = True

from django.db import IntegrityError, DatabaseError
from nodeshot.models import *

community = cmdgen.CommunityData('my-agent', 'public', 0)
pingcmd = "ping -c 1 %s > /dev/null"
MAX_THREAD_N = 1
interface_list = []
mutex = threading.Lock()
mac_string = "%02X:%02X:%02X:%02X:%02X:%02X"

oids = {'device_name': {'oid': (1,3,6,1,2,1,1,5,0), 'query_type': 'get',  'pos' : (3,0,1) },
        'device_type': {'oid': (1,2,840,10036,3,1,2,1,3,7), 'query_type': 'get',  'pos' : (3,0,1) },
        'ssid': {'oid': (1,3,6,1,4,1,14988,1,1,1,1,1,5), 'query_type': 'next',  'pos' : (3,0,0,1) },
        'frequency': {'oid': (1,3,6,1,4,1,14988,1,1,1,1,1,7), 'query_type': 'next',  'pos' : (3,0,0,1) },
        }

def get_mac(ip):
    'return the wifi mac of the device, else None'
    global community
    oid_mac = 1,3,6,1,2,1,2,2,1,6,7 # mac of ath0 
    transport = cmdgen.UdpTransportTarget((ip, 161))
    res = cmdgen.CommandGenerator().getCmd(community, transport, oid_mac)
    try:
        m = struct.unpack('BBBBBB', str(res[3][0][1]) )
        return mac_string % m
    except:
        return None


def get_signal(ip):
    'return a tuple of all the mac address associated and their signal'
    global community
    transport = cmdgen.UdpTransportTarget((ip, 161))
    oid_dbm = 1,3,6,1,4,1,14988,1,1,1,2,1,3
    #get connected mac and their dbm
    res = cmdgen.CommandGenerator().nextCmd(community, transport, oid_dbm)
    ret = []
    try:
        for i in res[3]:
            dbm = i[0][1]
            mac_addr_str = i[0][0][-7:-1]
            mac_addr = mac_string % tuple([int(i.strip()) for i in str(mac_addr_str)[1:-1].split(',')])
            print "got signal:", mac_addr, dbm
            ret.append( (mac_addr, dbm) )
        return ret
    except:
        return [] 


def get_simple_values(ip):
    'Get simple string values from smnp from the uid, return a dictionary'
    global community, oids_get, oids_next
    transport = cmdgen.UdpTransportTarget((ip, 161))
    ret = {}
    for name, oid_info in oids.items():
        if oid_info['query_type'] == 'get':
            result = cmdgen.CommandGenerator().getCmd(community, transport, oid_info['oid'])
        elif oid_info['query_type'] == 'next':
            result = cmdgen.CommandGenerator().nextCmd(community, transport, oid_info['oid'])
        try:
            for pos in oid_info['pos']:
                result = result[pos]
            ret[name] = str(result)
        except:
            ret[name] = None 
    return ret

class SNMPBugger(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self, name="ComputeThread-%d" % (id,))
    def run(self):
        while len(interface_list) > 0:
            mutex.acquire()
            inf = interface_list.pop() 
            mutex.release()
            ip = inf.ipv4_address
            # this is not necessary as is taken care at model level by django (is not possible to insert two interfaces with same IPv4 or IPv6)
            #if Interface.objects.filter(ipv4_address = ip).count() > 2:
            #    print "Error! DUPLICATE IP ADDRESS FOR IP: %s" % ip
            #    raise Exception
            # check via ping if device is up
            ping_status = os.system(pingcmd % ip) # 0-> up , >1 down
            try:
                device = inf.device
                node = inf.device.node
            except:
                # why?
                node = None 
                device = None

            if ping_status == 0: #node answers to the ping
                mac = get_mac(ip)
                # same as before - duplicate are avoided by django, no need to check
                #if mac and Interface.objects.filter(mac_address = mac).count() > 1:
                #    print "Error! MULTIPLE INTERFACE WITH THE SAME MAC ADDRESS"
                #    continue
                #if mac:
                #    # in case this mac is associated to another interface (strange situation, should not occour!)
                #    i = Interface.objects.filter(mac_address = mac).select_related().get()
                #    device = i.device
                #    node = i.device.node
                #else:
                i = inf

                # status of the node shall not be changed
                #if node:
                #    node.status = 'a'
                if device:
                    mac_signals = get_signal(ip)
                    # populate the signal information for each link
                    for m,s in mac_signals:
                        print 'macsignal:',m,s,i.ipv4_address
                        try:
                            link_to = Interface.objects.filter(mac_address = m).get()
                        except:
                            link_to = None
                        link_from = i 
                        if link_to:
                            if Link.objects.filter(from_interface = link_from, to_interface = link_to).count() == 1:
                                l = Link.objects.get(from_interface = link_from, to_interface = link_to)
                                l.dbm = s 
                                l.save()
                            elif Link.objects.filter(from_interface = link_to, to_interface = link_from).count() == 1:
                                l = Link.objects.get(from_interface = link_to, to_interface = link_from)
                                l.dbm = s 
                                l.save()
                            else:
                                Link(from_interface = link_from, to_interface = link_to, dbm = s).save()
                        else:
                            print "<-> Can not find an interface with mac %s" % m

                        # calculate the maximum signal (maybe useless?)
                        #signals = [s[1] for s in mac_signals] 
                        #m_max = max(signals) if len(signals) else 0  
                        #print "-------- Max signal is %d" % m_max
                        #if m_max > device.max_signal or device.max_signal == 0:
                        #    device.max_signal = m_max 

                    # populate device name, type, ssid and frequency    
                    smtp_values = get_simple_values(ip)
                    device_name =  smtp_values['device_name'] #get device name
                    device_type = smtp_values['device_type'] #get device type 
                    ssid = smtp_values['ssid'] #get ssid 
                    frequency = smtp_values['frequency'] #get frequency 
                    if device_name:
                        device.name = device_name
                        print "Device name: " + device_name
                    if device_type:
                        device.type = device_type
                        print "Device type: " + device_type
                    if ssid:
                        print "SSID = " + ssid
                        i.ssid = ssid
                    if frequency:
                        print "FREQUENCY = " + frequency 
                        i.wireless_channel = frequency
                    try:
                        device.save() #save
                    except IntegrityError:
                        print 'Integrity error for device %s' % device.name
                if mac:
                    i.mac_address = mac 
                    print mac
                    print "Node %s is up with mac %s" % ( ip, mac )
                else:
                    i.mac_address = None
                    print "Node %s is up but couldn't retrieve mac via snmp" % ip
                i.status = 'r'
                try:
                    i.save() #save
                except IntegrityError:
                    print 'Integrity error for interface %s of device %s' % (i, device.name)
            else:
                # interface does not answer to ping
                print "Node %s is down" % ip
                inf.status = 'u'
                inf.save()
                # don't change node status
                #node.status = 'd'
                
            if node:
                node.save() #save

def main():
    for i in Interface.objects.all():
        interface_list.append(i)

    for i in range(0, MAX_THREAD_N):
        SNMPBugger(i, ).start()
            
    try:
        from nodeshot.signals import clear_cache
        clear_cache()
    except:
        pass

if __name__ == "__main__":
        main()
