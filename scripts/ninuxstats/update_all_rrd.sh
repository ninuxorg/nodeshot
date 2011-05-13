#!/bin/bash
APP_DIR="/home/ninux/nodeshot/scripts/ninuxstats/"
cd $APP_DIR
for i in $(/sbin/route -n | grep 172.16. | grep 255.255.255.255 | awk '{print $1}'); do 
	./update_rrd.sh $i > rrd.log 2> rrd.err& 
done
