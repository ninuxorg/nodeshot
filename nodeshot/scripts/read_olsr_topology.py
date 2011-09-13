#!/usr/bin/env python

import urllib2, sys, os

# determine directory automatically
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.abspath(os.path.join(directory, os.path.pardir, os.path.pardir))
sys.path.append(parent)

import settings
from django.core.management import setup_environ 
setup_environ(settings)
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
                    # we need a new id
                    newid = self.idcounter
                    self.idcounter -= 1
                    self.aliasdict.update({ip: newid, alias: newid})
        def getIdFromIP(self, ip):
            if self.aliasdict.has_key(ip):
                return self.aliasdict[ip] 
            else:
                return 666
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
            self.topologylines = urllib2.urlopen(TOPOLOGY_URL).readlines()
            print ("Done...")
            self.linklist = list()
            self.aliasmanager = AliasManager()
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
            
            # parse MID info
            print ("Parsing MID Information...")
            while line.find('Table: MID') == -1:
                i += 1
                line = self.topologylines[i]

            i += 1 # skip the heading line
            line = self.topologylines[i]
            while not line.isspace():
                try:
                        ipaddr, alias = line.split()
                        self.aliasmanager.addalias(ipaddr, alias)
                except ValueError:
                        pass 
                i+=1
                line = self.topologylines[i]

            #debug
            print self.linklist

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


if __name__ == "__main__":
        TOPOLOGY_URL="http://127.0.0.1:2006/all"
        tp = TopologyParser(TOPOLOGY_URL)
        tp.parse()
        tp.process()
        print tp.linkdict
        for v in tp.linkdict.values():
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
                            l = saved_links[0]
                            l.etx = etx
                            l.save()
                            found = True
                        else:
                            fi = Interface.objects.filter(ipv4_address = ipA)
                            to = Interface.objects.filter(ipv4_address = ipB)
                            if fi.count() == 1 and to.count() == 1:
                                if fi.get().device.node != to.get().device.node:
                                    Link(from_interface = fi.get(), to_interface = to.get(), etx = etx).save()	
                                    found = True


