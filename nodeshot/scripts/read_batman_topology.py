#!/usr/bin/env python
TOPOLOGY_URLS=[ "http://eigenlab.org/battxtinfo.php" ]

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

for topology_url in TOPOLOGY_URLS:
    topologylines = urllib2.urlopen(topology_url).readlines()
    for line in topologylines:
        row_elements = line.split()
        if len(row_elements) == 5:
            # this is a good row
            macA, macB, cost = row_elements[0], row_elements[1], row_elements[4]
            print macA + "<-->" + macB +" : " + cost
            saved_links =  Link.objects.filter(Q(from_interface__mac_address=macA , to_interface__mac_address=macB ) |  Q(from_interface__mac_address=macB , to_interface__mac_address=macA ))
            if saved_links.count() > 0:
                # if a link already exists, just update
                l.etx = cost
                l.save()
            else:
                # otherwise create the new link
                fi = Interface.objects.filter(mac_address = macA)
                to = Interface.objects.filter(mac_address = macB)
                if fi.count() == 1 and to.count() == 1:
                       if fi.get().device.node != to.get().device.node:
                           # create a link if the neighbors are NOT on the same node
                           Link(from_interface = fi.get(), to_interface = to.get(), etx = cost).save()	


