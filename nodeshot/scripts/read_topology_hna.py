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

TOPOLOGY_URLS=["http://eigenlab.org/battxtinfo.php", "http://coppermine.eigenlab.org/battxtinfo.php"]

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
            print ("Retrieving topology...")
            try:
                self.topologylines = urllib2.urlopen(TOPOLOGY_URL).readlines()
            except Exception, e:
                print "Got exception: ", e
            print ("Done...")
            self.linklist = list()
            self.aliasmanager = AliasManager()
            self.hnalist = list()
        def parse(self):
            "parse the txtinfo plugin output and make two lists: a link list and an alias (MID) list"
            # parse Topology info
            print ("Parsing Toplogy Information...")
            i = 0
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
                        pass
                i+=1
                line = self.topologylines[i]

            j = i
            # parse HNA info
            print ("Parsing HNA Information...")
            while i < self.topologylines and line.find('Table: HNA') == -1:
                i += 1
                line = self.topologylines[i]

            if i < self.topologylines:
                i += 1 # skip the heading line
                line = self.topologylines[i]
                while not line.isspace():
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
            while i < self.topologylines and line.find('Table: MID') == -1:
                i += 1
                line = self.topologylines[i]

            if i >= self.topologylines:
                return

            i += 1 # skip the heading line
            line = self.topologylines[i]
            while i < self.topologylines and not line.isspace():
                try:
                        ipaddr, alias = line.split()
                        self.aliasmanager.addalias(ipaddr, alias)
                except ValueError:
                        pass
                i+=1
                line = self.topologylines[i]

            #debug
            #print self.linklist

        def process(self):
            "should be called after calling parse()"
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
                    self.linkdict.update({k: (iplist1, iplist2, etxx)} )
                else:
                    self.linkdict.update({k: (iplist1, iplist2, etx)} )

            self.hnainfo = list()
            for ipaddress, hna in self.hnalist:
                iplist = self.aliasmanager.getAliasesFromIP(ipaddress)
                self.hnainfo.append( (iplist, hna) )

#OLSR
if __name__ == "__main__":
    #Link.objects.all().delete()
    TOPOLOGY_URL="http://127.0.0.1:2006/all"
    try:
        tp = TopologyParser(TOPOLOGY_URL)
        tp.parse()
        tp.process()
        values = tp.linkdict.values()
        # values is a list of tuples with two ip lists
        # example is: ([1.2.3.4,5.6.7.8],[9.10.11.12]) 
        # first list contains all the addresses of a node
        # second list contains all the addresses the node of the other endpoint of a link 
        hnas = tp.hnainfo # list of tuples "ip list" , "hna"
    except Exception, e:
        print "Got exception: ", e
        values = False
    old_links = dict([ (l.id, False) for l in Link.objects.all()])
    #print tp.linkdict
    # record nodes
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
                            elif fi.count() > 1 or to.count() >1:
                                print "Anomaly: More than one interface for ip address"
                                print fi, to
    # record hnas
    old_hnas = dict([ (h.id, False) for h in Hna.objects.all()])

    for ips,hna in hnas:
        found_device,i  = None, None 
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
                old_hnas[h.get().id] = True
        
    #delete old hnas
    for h,v in old_hnas.iteritems() :
        if not v:
            Hna.objects.get(id=h).delete()
            print "Deleted hna %d" % h

    # BATMAN
    for topology_url in TOPOLOGY_URLS:
        try:
            topologylines = urllib2.urlopen(topology_url).readlines()
        except Exception, e:
            print "Got exception: ", e
        for line in topologylines:
            row_elements = line.split()
            if len(row_elements) == 5:
                # this is a good row
                macA, macB, cost = row_elements[0], row_elements[1], row_elements[4]
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
                    if fi_count > 2 or to_count > 2:
                        print "Anomality detected, two interface with same mac"
                        print fi, to
                    if 0 < fi_count < 2 and 0 < to_count < 2:
                        if fi.get().device.node != to.get().device.node:
                            # create a link if the neighbors are NOT on the same node
                            try:
                                l = Link(from_interface = fi.get(), to_interface = to.get(), etx = cost).save()
                                print 'Saved new link %s' % l
                            except:
                                print 'Error while saving link from %s to %s' % (fi.device.node, to.device.node)

    for l,v in old_links.iteritems() :
        if not v:
            Link.objects.get(id=l).delete()
            print "Deleted link %d" % l

