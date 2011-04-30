#!/bin/bash
snmpwalk -c public -v1 $1 -On .1.3.6.1.4.1.14988.1.1.1.2.1.3 | awk -F"."
'{for(i=15;i<20;i++)printf("%lx:",$i); printf("%lx ",$20); print $NF}' |
awk '{print $1,$NF}'

