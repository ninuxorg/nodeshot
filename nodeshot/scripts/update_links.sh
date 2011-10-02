#!/bin/bash
source ../../venv/bin/activate
DJANGO_SETTINGS_MODULE=settings ./read_olsr_topology.py
DJANGO_SETTINGS_MODULE=settings ./snmp.py
