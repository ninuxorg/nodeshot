#!/bin/bash
INTERFACE="ath0"
ping -c 1 $1 > /dev/null
if [ $? -eq 0 ]; then
	DATA_DIR="rrds/"
	#IFINDEX=`snmpwalk -c public -v1 $1 -On .1.3.6.1.2.1.2.2.1.2 | grep ${INTERFACE} | awk -F"\.| " '{print $12}'`
	IFINDEX=$(snmpwalk -c public -v1 $1 -On .1.3.6.1.2.1.2.2.1.2 | grep ${INTERFACE} |  awk -F'.' '{print $12}' | awk '{print $1}')
	IN=$(snmpwalk -c public -v1 $1 -On .1.3.6.1.2.1.2.2.1.10.${IFINDEX} | awk '{print $NF}')
	OUT=$(snmpwalk -c public -v1 $1  -On .1.3.6.1.2.1.2.2.1.16.${IFINDEX} | awk '{print $NF}')
	FILENAME=${DATA_DIR}${1}.rrd
	if [ ! -e $FILENAME ]; then 
		rrdtool create -b 946684800 ${FILENAME} DS:out:COUNTER:600:U:U DS:in:COUNTER:600:U:U RRA:LAST:0.5:1:8640 RRA:AVERAGE:0.5:6:600 RRA:AVERAGE:0.5:24:600 RRA:AVERAGE:0.5:288:600;
	fi
	rrdtool update ${FILENAME} $(date +%s):$OUT:$IN
fi



