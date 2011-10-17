#!/bin/bash
# Just put this file in crontab to execute all the scripts periodically
# We use python virtual environment (venv) but you couldn't have such need. In that case just comment the folling line.
#source ../../venv/bin/activate
#get ETX of all the links
DJANGO_SETTINGS_MODULE=settings /home/ninux/nodeshot/venv/bin/python /home/ninux/nodeshot/nodeshot/scripts/read_topology.py
#DJANGO_SETTINGS_MODULE=settings /home/ninux/nodeshot/venv/bin/python /home/ninux/nodeshot/nodeshot/scripts/read_batman_topology.py
#poll nodes to get or update information through snmp
DJANGO_SETTINGS_MODULE=settings /home/ninux/nodeshot/venv/bin/python /home/ninux/nodeshot/nodeshot/scripts/update_db.py
