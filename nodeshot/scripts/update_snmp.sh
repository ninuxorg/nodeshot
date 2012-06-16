#!/bin/bash
# Just put this file in crontab to execute all the scripts periodically
# We use python virtual environment (venv) but you couldn't have such need. In that case just comment the folling line.
#source ../../venv/bin/activate
#DJANGO_SETTINGS_MODULE=settings /home/ninux/nodeshot/venv/bin/python /home/ninux/nodeshot/nodeshot/scripts/snmp.py
DJANGO_SETTINGS_MODULE=settings /home/ninux/nodeshot/venv/bin/python /home/ninux/nodeshot/nodeshot/scripts/snmpv6.py
DJANGO_SETTINGS_MODULE=settings /home/ninux/nodeshot/venv/bin/python /home/ninux/nodeshot/nodeshot/scripts/update_db.py
