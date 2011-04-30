from pysnmp.entity.rfc3413.oneliner import cmdgen

community = cmdgen.CommunityData('my-agent', 'public', 0)
transport = cmdgen.UdpTransportTarget(('172.16.141.2', 161))
oid = 1,3,6,1,4,1,14988,1,1,1,2,1,3
res = cmdgen.CommandGenerator().nextCmd(community, transport, oid)
for i in res[3]:
    dbm = i[0][1]
    mac_addr = i[0][0][-6:]
    mac_addr = "%X:%X:%X:%X:%X:%X" % tuple([int(i.strip()) for i in str(mac_addr)[1:-1].split(',')])
    print mac_addr, dbm
