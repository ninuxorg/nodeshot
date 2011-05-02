from pysnmp.entity.rfc3413.oneliner import cmdgen
import sys, os, struct, threading
sys.path.append("/home/ninux/nodeshot")

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import IntegrityError, DatabaseError
from ns.models import *

community = cmdgen.CommunityData('my-agent', 'public', 0)
pingcmd = "ping -c 1 "
MAX_THREAD_N = 100
interface_list = []
mutex = threading.Lock()

def get_mac(ip):
    'return the wifi mac of the device, else None'
    global community
    oid_mac = 1,3,6,1,2,1,2,2,1,6,7
    transport = cmdgen.UdpTransportTarget((ip, 161))
    res = cmdgen.CommandGenerator().getCmd(community, transport, oid_mac)
    try:
        m = struct.unpack('BBBBBB', str(res[3][0][1]) )
        return "%X:%X:%X:%X:%X:%X" % m  
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
            mac_addr_str = i[0][0][-6:]
            mac_addr = "%X:%X:%X:%X:%X:%X" % tuple([int(i.strip()) for i in str(mac_addr_str)[1:-1].split(',')])
            print mac_addr, dbm
            ret.append( (mac_addr, dbm) )
        return ret
    except:
        return [] 


def get_name(ip):
    'return the name of the device'
    global community
    oid = 1,3,6,1,2,1,1,5,0
    transport = cmdgen.UdpTransportTarget((ip, 161))
    res = cmdgen.CommandGenerator().getCmd(community, transport, oid)
    try:
        name = str(res[3][0][1])
        return name
    except:
        return None


def get_device_type(ip):
    global community
    oid = 1,2,840,10036,3,1,2,1,3,7
    transport = cmdgen.UdpTransportTarget((ip, 161))
    res = cmdgen.CommandGenerator().getCmd(community, transport, oid)
    try:
        name = str(res[3][0][1])
        return name
    except:
        return None

class SNMPBugger(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self, name="ComputeThread-%d" % (id,))
    def run(self):
        while len(interface_list) > 0:
            mutex.acquire()
            i = interface_list.pop() 
            mutex.release()
            ip = i.ipv4_address
            # check via ping if device is up
            ping_status = os.system(pingcmd + ip) # 0-> up , >1 down
            try:
                node = i.device.node
            except:
                node = None 

            try:
                device = i.device
            except:
                device = None

            if ping_status == 0:
                if node:
                    node.status = 'a'
                mac = get_mac(ip)
                if device:
                    signals = [s[1] for s in get_signal(ip)] 
                    m_max = max(signals) if len(signals) else 0  #get max signals
                    print "-------- Max signal is %d" % m_max
                    device.max_signal = m_max 
                    device_name = get_name(ip) #get device name
                    device_type = get_device_type(ip) #get device name
                    if device_name:
                        device.name = device_name
                        print "Device name: " + device_name
                    if device_type:
                        device.type = device_type
                    device.save() #save
                if mac:
                    i.mac_address = mac 
                    print mac
                    print "Nodo %s up con mac %s" % ( ip, mac )
                else:
                    i.mac_address = ''
                    print "Nodo %s up ma niente mac via snmp" % ip
                i.save() #save
            else:
                print "Nodo %s down" % ip
            if node:
                node.save() #save



def main():
    for node in Node.objects.all():
        #reset status of all the node to potential
        node.status = 'p'
        node.save()

    for i in Interface.objects.all():
        interface_list.append(i)

    for i in range(0, MAX_THREAD_N):
            SNMPBugger(i, ).start()

if __name__ == "__main__":
        main()
