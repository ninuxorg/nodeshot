#!/bin/bash
# Just put this file in crontab to execute all the scripts periodically
# We use python virtual environment (venv) but you couldn't have such need. In that case just comment the folling line.
source ../../venv/bin/activate
#get ETX of all the links
DJANGO_SETTINGS_MODULE=settings ./read_olsr_topology.py
DJANGO_SETTINGS_MODULE=settings ./read_batman_topology.py
#poll nodes to get or update information through snmp
#DJANGO_SETTINGS_MODULE=settings ./snmp.py
DJANGO_SETTINGS_MODULE=settings ./update_db.py