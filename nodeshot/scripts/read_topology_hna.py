#!/usr/bin/env python

import urllib2, sys, os

# determine directory automatically
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.abspath(os.path.join(directory, os.path.pardir, os.path.pardir))
sys.path.append(parent)

import settings
from django.core.management import setup_environ
setup_environ(settings)
__builtins__.IS_SCRIPT = True
from nodeshot.models import *
from django.db.models import Q

# Take all ips of a node with MID olsr, for any couple of node composing a link, so [ip1A,ip2A,ip3A] <--> [ip1B,ip2B]
# query db for existing link from one ip of A to one ip of B (break ties randomly). Else create a new one
# write etx on the etx attribute of the Link object
# Link quality thresholds

class AliasManager(object):
        "a MID is an IP alias in OLSR terminology. This class manages all IP addresses"
        def __init__(self):
            self.aliasdict = dict() # keys are ip addresses, values are unique ids
            self.idcounter = -2     # -1 is reserved, we start from -2
            self.unknownIPs = list()
        def addalias(self, ip, alias):
            # all aliases of the same ip share the same unique id, stored as value of aliasdict.
            if self.aliasdict.has_key(ip):
                    # if we already have this ip, use the same id for the alias
                    ipid = self.aliasdict[ip]
                    self.aliasdict.update({alias: ipid})
            elif self.aliasdict.has_key(alias):
                    # if we already have this alias, use the same id for the ip
                    ipid = self.aliasdict[alias]
                    self.aliasdict.update({ip: ipid})
            else:
                    # if a link already exists, update
                    # we need a new id
                    newid = self.idcounter
                    self.idcounter -= 1
                    self.aliasdict.update({ip: newid, alias: newid})
        def getIdFromIP(self, ip):
            if self.aliasdict.has_key(ip):
                    return self.aliasdict[ip]
            else:
                    self.idcounter -= 1
                    newid = self.idcounter
                    self.aliasdict.update({ip: newid})
                    return newid
        def getAliasesFromIP(self, ipaddr):
            id = self.getIdFromIP(ipaddr)
            r = [ip for ip in self.aliasdict.keys() if self.aliasdict[ip] == id]
            if not ipaddr in r:
                r.append(ipaddr)
            return r
        def __str__(self):
            return str(self.aliasdict)


class TopologyParser(object):
        def __init__(self, topology_url):
            self.topology_url = topology_url
            print ("Retrieving topology from %s ..." % topology_url)
            try:
                req = urllib2.Request(self.topology_url, data=None, headers={'User-agent' : 'Wget/1.12'})
                self.topologylines = urllib2.urlopen(req, timeout=settings.TOPOLOGY_URL_TIMEOUT).readlines()
            except Exception, e:
                print "Got exception: ", e
                self.topologylines = []
            print ("Done...")
            self.linklist = list()
            self.aliasmanager = AliasManager()
            self.hnalist = list()
        def parse(self):
            "parse the txtinfo plugin output and make two lists: a link list and an alias (MID) list"
            # parse Topology info
            print ("Parsing Topology Information of %s ..." % self.topology_url)
            i = 0
            line = self.topologylines[i]

            while line.find('Table: Links') == -1:
                i += 1
                line = self.topologylines[i]

            i += 2 # skip the heading line
            line = self.topologylines[i]
            while not line.isspace():
                try:
                        ipaddr1, ipaddr2, hyst, lq, nlq, etx = line.split()
                        self.linklist.append((ipaddr1, ipaddr2, float(etx)))
                except ValueError:
                        print ("wrong line or INFINITE ETX: %s" % line)
                        pass
                i+=1
                line = self.topologylines[i]

            while line.find('Table: Topology') == -1:
                i += 1
                line = self.topologylines[i]

            i += 2 # skip the heading line
            line = self.topologylines[i]
            while not line.isspace():
                try:
                        ipaddr1, ipaddr2, lq, nlq, etx = line.split()
                        self.linklist.append((ipaddr1, ipaddr2, float(etx)))
                except ValueError:
                        print ("wrong line or INFINITE ETX: %s" % line)
                        pass
                i+=1
                line = self.topologylines[i]

            j = i + 1
            # parse HNA info
            print ("Parsing HNA Information...")
            while i < len(self.topologylines) and line.find('Table: HNA') == -1:
                line = self.topologylines[i]
                i += 1

            if i < len(self.topologylines):
                i += 1 # skip the heading line
                line = self.topologylines[i]
                while not line.isspace() and i < len(self.topologylines):
                    try:
                            hna, announcer = line.split()
                            self.hnalist.append((announcer, hna))
                    except ValueError:
                            pass
                    i+=1
                    line = self.topologylines[i]
            else:
                i = j


            # parse MID info
            print ("Parsing MID Information...")
            while i < len(self.topologylines) and line.find('Table: MID') == -1:
                line = self.topologylines[i]
                i += 1

            if i >= len(self.topologylines):
                return

            i += 1 # skip the heading line
            line = self.topologylines[i]
            while i < len(self.topologylines) and not line.isspace():
                try:
                        ipaddr, aliases = line.split()
                        for alias in aliases.split(';'):
                            self.aliasmanager.addalias(ipaddr, alias)
                except ValueError:
                        pass
                i+=1
                line = self.topologylines[i]

            #debug
            #print self.linklist

        def process(self, etx_threshold=23.0):
            "should be called after calling parse(). etx_threshold is the ETX threshold above which links are excluded"
            self.linkdict = dict()
            for ipaddr1, ipaddr2, etx in self.linklist:
                id1 = self.aliasmanager.getIdFromIP(ipaddr1)
                id2 = self.aliasmanager.getIdFromIP(ipaddr2)
                iplist1 = self.aliasmanager.getAliasesFromIP(ipaddr1)
                iplist2 = self.aliasmanager.getAliasesFromIP(ipaddr2)
                if id1 < id2:
                    k = (id1, id2)
                else:
                    k = (id2, id1)
                    # swap
                    iplistmp = iplist1
                    iplist1 = iplist2
                    iplist2 = iplistmp

                #debug
                if len(iplist1) == 0 or len(iplist2) == 0:
                    print "DDDDD", ipaddr1,ipaddr2,etx

                if self.linkdict.has_key(k):
                    etx0 = self.linkdict[k][2]
                    etxx = (etx0 + etx) * 0.5 # average
                    finaletx = etxx
                else:
                    finaletx = etx
                if finaletx <= etx_threshold: # probably a vpn link
                    self.linkdict.update({k: (iplist1, iplist2, finaletx)} )

            self.hnainfo = list()
            for ipaddress, hna in self.hnalist:
                iplist = self.aliasmanager.getAliasesFromIP(ipaddress)
                self.hnainfo.append( (iplist, hna) )

def isinsubnet(ip, subnet, mask_threshold):
    """
    Check if the IPv4 address "ip" is in the given subnet "subnet".
    If the subnet mask is less than "mask_threshold" then return False.

    """
    # validation
    if ip == None or subnet == None or len(ip) < 7 or len(subnet) < 9:
        return False
    # TODO: more validation
    # separate the net from the netmask
    net = subnet.split("/")[0]
    mask = int(subnet.split("/")[1])
    # check if the mask is below mask_threshold
    if mask < mask_threshold:
        return False
    # convert the net into an int
    netb = [int(b) for b in net.split(".")]
    intnet = sum([octect << lshift for (octect, lshift) in zip(netb, range(24, -1, -8))])
    # convert the netmask into an int
    maskbits = [1] * mask
    intmask = sum([octect << lshift for (octect, lshift) in zip(maskbits, range(31, 31 - mask, -1))])
    # convert the IPv4 address into an int
    ipb = [int(b) for b in ip.split(".")]
    intip = sum([octect << lshift for (octect, lshift) in zip(ipb, range(24, -1, -8))])

    return intip & intmask == intnet & intmask


#OLSR
if __name__ == "__main__":
    HNA_NETMASK_THRESHOLD = 20 #don't consider HNAs with a netmask less than than this value
    HNA_COUNT_THRESHOLD = 12 #don't draw links between nodes and remote HNAs if the number of HNAs is bigger than this value
    #Link.objects.all().delete()
    hnas = []
    values = []
    for OLSR_URL in settings.OLSR_URLS:
        try:
            tp = TopologyParser(OLSR_URL)
            tp.parse()
            tp.process(etx_threshold=settings.ETX_THRESHOLD)
            values += tp.linkdict.values()
            # values is a list of tuples with two ip lists
            # example is: ([1.2.3.4,5.6.7.8],[9.10.11.12])
            # first list contains all the addresses of a node
            # second list contains all the addresses the node of the other endpoint of a link
            hnas += tp.hnainfo # list of tuples "ip list" , "hna"
        except Exception, e:
            print "Got exception: ", e
            #values = False
        old_links = dict([ (l.id, False) for l in Link.objects.all()])
        #print tp.linkdict
    # record nodes
    activenodes = set()
    if values:
        for v in values:
            ipsA, ipsB, etx = v
            found = False
            if len(ipsA) <= 0 and len(ipsB) <=0:
                continue
            for a in range(0,len(ipsA)):
                for b in range(0,len(ipsB)):
                    if not found:
                        ipA, ipB = ipsA[a], ipsB[b]
                        saved_links =  Link.objects.filter(Q(from_interface__ipv4_address=ipA , to_interface__ipv4_address=ipB ) |  Q(from_interface__ipv4_address=ipB , to_interface__ipv4_address=ipA ))
                        if saved_links.count() > 0:
                            # if a link already exists, update
                            l = saved_links[0]
                            if not l.from_interface.draw_link or not l.to_interface.draw_link:
                                continue
                            l.etx = etx
                            l.save()
                            old_links[l.id] = True
                            found = True
                            print "Updated link: %s" % l
                            activenodes.add(l.from_interface.device.node.id)
                            activenodes.add(l.to_interface.device.node.id)
                        else:
                            # otherwise create a new link
                            fi = Interface.objects.filter(ipv4_address = ipA).exclude(type='vpn').exclude(draw_link=False)
                            to = Interface.objects.filter(ipv4_address = ipB).exclude(type='vpn').exclude(draw_link=False)
                            if fi.count() == 1 and to.count() == 1:
                              # create a link if the neighbors are NOT on the same node
                              #print fi, fi.get().id, to, to.get().id
                              if fi.get().device.node != to.get().device.node:
                                l = Link(from_interface = fi.get(), to_interface = to.get(), etx = etx).save()
                                print "Saved new link: %s" % l
                                found = True
                                activenodes.add(fi.get().device.node.id)
                                activenodes.add(to.get().device.node.id)
                            elif fi.count() > 1 or to.count() >1:
                                print "Anomaly: More than one interface for ip address"
                                print fi, to

    # record hnas
    old_hnas = dict([ (h.id, False) for h in Hna.objects.all()])

    for ips, hna in hnas:
        found_device, i  = None, None
        for ip in ips:
            if not found_device:
                i = Interface.objects.filter(ipv4_address = ip)
                found_device = i.count() > 0
        if found_device:
            h = Hna.objects.filter(device = i.get().device).filter(route = hna)
            if h.count() <= 0:
                new_hna = Hna(device = i.get().device, route = hna)
                new_hna.save()
            else:
                old_hnas[h[0].id] = True

    #delete old hnas
    for h,v in old_hnas.iteritems() :
        if not v:
            Hna.objects.get(id=h).delete()
            print "Deleted hna %d" % h
    
    # take into account L2 only / bridged links
    # iterate over all devices, and see if the IP address of one of the interfaces belongs to an HNA

    l2links = []
    for interface in Interface.objects.all().exclude(type='vpn').exclude(draw_link=False):
        for hna in Hna.objects.all().exclude(route="0.0.0.0/0"):
            if isinsubnet(interface.ipv4_address, hna.route, HNA_NETMASK_THRESHOLD):
                try:
                    # get one interface associated to this HNA
                    hna_device_interface = hna.device.interface_set.all()[0]
                    nodeA = interface.device.node
                    nodeB = hna_device_interface.device.node
                except:
                    continue
                # check if source and destination are on the same node
                if nodeA == nodeB:
                    continue
                # check if we are linking an active node on the HNA side
                if not nodeB.id in activenodes:
                    print "Node %s is not active" % nodeB
                    continue
                if nodeB.status in "pu" or nodeA.status in "pu":
                    print "Node %s or %s is not active" % (nodeA, nodeB)
                    continue
                if hna.device.hna_set.count() > HNA_COUNT_THRESHOLD:
                    print "HNA %s is from a device with too many HNAs [%s]. Ignoring." % (hna.route, hna.device.node)
                    continue

                # check if the link already exists
                if Link.objects.filter(Q(from_interface__device__node__id = nodeA.id, to_interface__device__node__id = nodeB.id) |\
                        Q(from_interface__device__node__id = nodeB.id, to_interface__device__node__id = nodeA.id)).count() > 1:
                    print "Link already exists: %s <--> %s" % (nodeA, nodeB)
                    continue
                # don't do this in nodeshot2
                if (nodeA.id, nodeB.id) in l2links or (nodeB.id, nodeA.id) in l2links:
                    print "Link already exists (inserted by us): %s <--> %s" % (nodeA, nodeB)
                    continue
                l = Link(from_interface = interface, to_interface = hna_device_interface, etx = 1.042)
                l.save()
                l2links.append((nodeA.id, nodeB.id))
                print "Found that %s is in %s. Added Link from %s to %s." % (interface.ipv4_address, hna.route, nodeA, nodeB)

    # BATMAN
    for topology_url in settings.BATMAN_URLS:
        try:
            print ("Opening URL %s" % topology_url)
            topologylines = urllib2.urlopen(topology_url, data=None, timeout=settings.TOPOLOGY_URL_TIMEOUT).readlines()
        except Exception, e:
            print ("A problem occurred: %s" % e)
            print ("Skipping to the next topology URL.")
            continue
        for line in topologylines:
            row_elements = line.split()
            if len(row_elements) == 5:
                # this is a good row
                macA, macB, cost = row_elements[0], row_elements[1], row_elements[4]
                try:
                    bat_etx = float(cost)
                except ValueError:
                    continue
                if bat_etx > settings.ETX_THRESHOLD: # probably a vpn link
                    continue
                print macA + "<-->" + macB +" : " + cost
                saved_links =  Link.objects.filter(Q(from_interface__mac_address=macA , to_interface__mac_address=macB ) |  Q(from_interface__mac_address=macB , to_interface__mac_address=macA ))
                # I think is better to use len(saved_links) than saved_links.count() cos it results in less hits to the database
                link_count = len(saved_links)
                if 0 < link_count < 2:
                    l = saved_links[0]
                    if not l.from_interface.draw_link or not l.to_interface.draw_link:
                        continue
                    # if a link already exists, just update
                    l.etx = cost
                    old_links[l.id] = True
                    l.save()
                    print "Updated etx to %s for link %s" % (cost, l)
                elif link_count > 1:
                    print "Anomaly: 2 links retrieved."
                elif link_count < 1:
                    # otherwise create the new link
                    fi = Interface.objects.filter(mac_address = macA).exclude(type='vpn').exclude(draw_link=False)
                    to = Interface.objects.filter(mac_address = macB).exclude(type='vpn').exclude(draw_link=False)
                    fi_count = len(fi)
                    to_count = len(to)
                    if fi_count >= 2 or to_count >= 2:
                        print "Anomality detected, two interface with same mac: " + macA + " (" + str(fi_count) + ") , " + macB + " (" + str(to_count) +")"
                    if 0 < fi_count < 2 and 0 < to_count < 2:
                        if fi.get().device.node != to.get().device.node:
                            # create a link if the neighbors are NOT on the same node
                            try:
                                l = Link(from_interface = fi.get(), to_interface = to.get(), etx = cost).save()
                                print 'Saved new link %s' % l
                            except:
                                print 'Error while saving link from %s to %s' % (fi.device.node, to.device.node)
                    else:
                        macA_debug =  Interface.objects.filter(mac_address = macA)
                        macB_debug =  Interface.objects.filter(mac_address = macB)
                        if len(macA_debug) == 0 or len(macB_debug) == 0:
                            print "Anomality detected: links between %s <-> %s: number of interfaces found %s <-> %s" % ( macA, macB, str(len(macA_debug)), str(len(macB_debug)) )
                        else:
                            print "Anomality detected: links between %s <-> %s: vpn?, draw_link? : %s, %s <-> %s, %s" % ( macA, macB, macA_debug[0].type, macA_debug[0].draw_link, macB_debug[0].type, macB_debug[0].draw_link)

    for l,v in old_links.iteritems() :
        if not v:
            try:
                Link.objects.get(id=l).delete()
            except Exception, e:
                print ("A problem occurred: %s" % e)
            print "Deleted link %d" % l

