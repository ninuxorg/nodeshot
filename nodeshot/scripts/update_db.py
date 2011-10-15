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

# update statistics (number of nodes and links)
from nodeshot.signals import update_statistics
update_statistics()

# clear static cache if necessary
try:
    from nodeshot.signals import clear_cache
    from staticgenerator import quick_publish
    clear_cache()
    # regenerate main pages
    quick_publish('/', 'nodes.json', 'jstree.json', 'nodes.kml', 'overview/')
except:
    pass
