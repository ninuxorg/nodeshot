#!/usr/bin/env python

import sys, os, re, struct, threading

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


print "Check for orphan interfaces..."

for i in Interface.objects.all():
    try:
        x = i.device.id
    except:
        print "interface %d is orphan" % i.id

print "Check for orphan devices..."

for d in Device.objects.all():
    try:
        x = d.node.id
    except:
        print "Device %d is orphan" % d.id

print "Check for orphan hnas..."

for h in Hna.objects.all():
    try:
        x = h.device.id
    except:
        print "Hna %d is orphan" % h.id

print "Check for orphan links..."

for l in Link.objects.all():
    try:
        x = l.from_interface.id
        x = l.to_interface.id
    except:
        print "Link %d is orphan" % l.id

