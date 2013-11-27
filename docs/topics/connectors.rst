**********
Connectors
**********

Prototypal abstraction layer to retrieve information from network devices.

====================
Console instructions
====================

Initialize DeviceLogin via command line::

    # cd into project directory
    cd [myproject]/  # eg: /var/django/nodeshot/projects/ninux    
    
    # activate virtual env
    source python/bin/activate
    
    # launch shell_plus
    python manage.py shell_plus

Now go on with the python shell commands::

    d = DeviceLogin()
    d.node_id = 1  # the node id which you want to test
    d.host = '172.16.177.25'  # the ip/hostname of the device you want to test
    d.username = 'root'
    d.password = 'yourpassword'
    d.port = 22  # default port is 22
    d.store = True  # if you want to store it in DB
    # path to the connector class you are testing
    d.connector_class = 'nodeshot.networking.connectors.ssh.OpenWRT'
    
    # open session with the protocol you're testing, in this case SSH
    d.connector.connect()
    
    # try some commands
    print d.connector.output('cat /etc/openwrt_release')
    
    # alternatively use a method specific of that class
    print d.connector.get_os()
    ('OpenWrt', 'Attitude Adjustment (Scooreggione v4 12.09, r36608)')
    
    # close connection when you're done
    d.connector.close()