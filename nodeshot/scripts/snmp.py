#!/usr/bin/env python

from pysnmp.entity.rfc3413.oneliner import cmdgen
import sys, os, re, struct, threading

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
from django.core.exceptions import ObjectDoesNotExist


community = cmdgen.CommunityData('my-agent', 'public', 0)
pingcmd = "ping -c 1 %s > /dev/null"
MAX_THREAD_N = 10
interface_list = []
mutex = threading.Lock()
mac_format = "%02X:%02X:%02X:%02X:%02X:%02X"

oids = {'device_name': {'oid': (1,3,6,1,2,1,1,5,0), 'query_type': 'get',  'pos' : (3,0,1) },
        'device_type': {'oid': (1,2,840,10036,3,1,2,1,3,7), 'query_type': 'get',  'pos' : (3,0,1) },
        'ssid': {'oid': (1,3,6,1,4,1,14988,1,1,1,1,1,5), 'query_type': 'next',  'pos' : (3,0,0,1) },
        'frequency': {'oid': (1,3,6,1,4,1,14988,1,1,1,1,1,7), 'query_type': 'next',  'pos' : (3,0,0,1) },
        }

def get_mac(ip, i_type):
    'return the wifi mac of the device, else None'
    global community
    transport = cmdgen.UdpTransportTarget((ip, 161))
    oid_mac = None
    # search for the right oid
    if i_type == "wifi" or i_type == "w": #db is dirty, both wifi and w occurrence
        try:
	    for i in range(0,10):
            	if cmdgen.CommandGenerator().getCmd(community, transport, (1,3,6,1,2,1,2,2,1,2,i)  )[3][0][1] == "ath0":
                	oid_mac = 1,3,6,1,2,1,2,2,1,6,i # mac of ath0
                	break
        except:
            pass 
    elif i_type == "eth" or i_type == "e":
        try:
            for i in range(0,10):
            	if cmdgen.CommandGenerator().getCmd(community, transport, (1,3,6,1,2,1,2,2,1,2,i)  )[3][0][1] == "eth0":
                	oid_mac = 1,3,6,1,2,1,2,2,1,6,i # mac of eth0
                	break
        except:
            pass 
    else:
        print "KO: Unknown interface type %s not eth or wifi" , i_type
        return None
    if not oid_mac:
        return None
    res = cmdgen.CommandGenerator().getCmd(community, transport, oid_mac)
    try:
        m = struct.unpack('BBBBBB', str(res[3][0][1]) )
        return mac_format % m
    except:
        return None



def get_signal(ip):
    'return a tuple of all the mac address of stations associated to that host and their signal'
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
            mac_addr = mac_format % tuple([int(i.strip()) for i in str(mac_addr_str).split('.')])
            ret.append( (mac_addr, dbm) )
        return ret
    except:
        return [] 


def get_simple_values(ip):
    '''Get simple string values from smnp from the uid, return a dictionary
       The list of oid, type of query (get or next) and the position of the result
       is contained in the oid dictionary'''
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
            # for each interface in interface_list ...
            mutex.acquire()
            inf = interface_list.pop() 
            mutex.release()
            ip = inf.ipv4_address
            # 1. check via ping if device is up
            ip_regexp = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
            if ip and len(ip) > 0 and ip_regexp.match(ip):
                ping_status = os.system(pingcmd % ip) # 0-> up , >1 down
            else:
                ping_status = 1 #invalid ip, maybe ipv6 or just mac
            if not ip or len(ip) <= 0:
                print "KO: Interface %d without ip (batman?)" % inf.id

            if ping_status == 0: #node answers to the ping
                device = inf.device
                node = inf.device.node
                # 2. retrieve the mac address
                mac = get_mac(ip, inf.type)
                if mac:
                    inf.mac_address = mac 
                    print "OK: Node %s is up with mac %s" % ( ip, mac )
                else:
                    inf.mac_address = None
                    print "KO: Node %s is up but couldn't retrieve mac via snmp (interface type is %s)" % (ip,inf.type)
                inf.status = 'r'
                try:
                    inf.save() #save
                except IntegrityError:
                    print 'ERROR: Integrity error for interface %s of device %s' % (inf, device.name)


                # 3. for each signal this node receives, set the dbm in the Link model
                mac_signals = get_signal(ip)
                for m,s in mac_signals:
                    print 'OK: SIGNAL of %s - %s dbm from %s' % ( ip, s, m )
                    try:
                        link_to = Interface.objects.filter(mac_address = m).get()
                    except:
                        link_to = None

                    if link_to:
                        if Link.objects.filter(from_interface = inf, to_interface = link_to).count() == 1:
                            l = Link.objects.get(from_interface = inf, to_interface = link_to)
                            l.dbm = s 
                            l.save()
                        elif Link.objects.filter(from_interface = link_to, to_interface = inf).count() == 1:
                            l = Link.objects.get(from_interface = link_to, to_interface = inf)
                            l.dbm = s 
                            l.save()
                    else:
                        print "KO: There are %d interfaces with mac %s" % (Interface.objects.filter(mac_address = m).count(), m)

                # 4. populate device name, type, ssid and frequency    
                smtp_values = get_simple_values(ip)
                device_name = smtp_values['device_name'] #get device name
                device_type = smtp_values['device_type'] #get device type 
                ssid = smtp_values['ssid'] #get ssid 
                frequency = smtp_values['frequency'] #get frequency 
                if device_name:
                    device.name = device_name
                    print "OK: Device name of " + ip + " : " + device_name
                if device_type:
                    device.type = device_type
                    print "OK: Device type of " + ip + " : " + device_type
                if ssid:
                    print "OK: SSID of " + ip + " : " + ssid
                    inf.ssid = ssid
                if frequency:
                    print "OK: Frequency of " + ip + " : " + frequency 
                    inf.wireless_channel = frequency
                try:
                    device.save() #save
                except IntegrityError:
                    print 'ERROR: Integrity error for device %s' % device.name
            else:
                # interface does not answer to ping
                print "KO: Interface %s is down" % ip
                inf.status = 'u'
                inf.save()

def main():
    for i in Interface.objects.all():
        interface_list.append(i)

    for i in range(0, MAX_THREAD_N):
        # launch MAX_THREAD_N threads to bug the network
        SNMPBugger(i, ).start()
            
    try:
        from nodeshot.signals import clear_cache
        clear_cache()
    except:
        pass

if __name__ == "__main__":
        main()
