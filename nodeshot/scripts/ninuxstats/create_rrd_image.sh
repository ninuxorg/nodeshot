RRD_DIR="/home/ninux/nodeshot/scripts/ninuxstats/rrds/"
WWW_DIR="/home/ninux/nodeshot/media/graphs/"
rrdtool graph ${WWW_DIR}$1.png --start -2d --end now --vertical-label bits/s --width 720 --height 140 --title "${1}" DEF:graph_out_pre=${RRD_DIR}${1}.rrd:out:LAST DEF:graph_in_pre=${RRD_DIR}${1}.rrd:in:LAST \
CDEF:graph_in_bytes=graph_in_pre,UN,0,graph_in_pre,IF \
CDEF:graph_out_bytes=graph_out_pre,UN,0,graph_out_pre,IF \
CDEF:graph_in=graph_in_bytes,8,* \
CDEF:graph_out=graph_out_bytes,8,* \
AREA:graph_in#078e00:"In Traffic" \
VDEF:maxin=graph_in,MAXIMUM \
VDEF:avin=graph_in,AVERAGE \
VDEF:lastin=graph_in_pre,LAST \
GPRINT:avin:" Av\: %.2lf %sbps" \
GPRINT:maxin:"Max\: %.2lf %sbps" \
GPRINT:lastin:"Last\: %.2lf %sbps\n" \
LINE1:graph_out#00468e:"Out Traffic " \
VDEF:maxout=graph_out,MAXIMUM \
VDEF:avout=graph_out,AVERAGE \
VDEF:lastout=graph_out_pre,LAST \
GPRINT:avout:"Av\: %.2lf %sbps" \
GPRINT:maxout:" Max\: %.2lf %sbps" \
GPRINT:lastout:"Last\: %.2lf %sbps\n"
