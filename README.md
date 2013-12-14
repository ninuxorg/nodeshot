                     _           _           _   
     _ __   ___   __| | ___  ___| |__   ___ | |_ 
    | '_ \ / _ \ / _` |/ _ \/ __| '_ \ / _ \| __|
    | | | | (_) | (_| |  __/\__ \ | | | (_) | |_ 
    |_| |_|\___/ \__,_|\___||___/_| |_|\___/ \__|


CURRENT STATUS
--------------

New refactored major version under active development here:
https://github.com/nemesisdesign/nodeshot/

Stay tuned.


A nice snapshot of your wireless community network
---------------------------------------------------------
Nodeshot is a web tool for wireless community network.  It allows
members to add their node and to share and manage information about
their configurations like devices, ip addresses, wireless parameters
etc. In this way, newcomers can easily contact/connect with them.

Internal scripts will update the topology and retrieve nodes information
via snmp, or parsing routing information given by olsr, batman or
whatever.

It is super-fast, nice and easy to use.

It rises from the ashes of WNMap (http://sourceforge.net/projects/wnmap/),
powered by django (https://www.djangoproject.com/), released
under GPLv3 and tested inside the Ninux wireless community network
(http://wiki.ninux.org/).


DEVELOPMENT INSTALLATION
---------------
If you want to do a quick install to play with nodeshot just follow this routine:

    git clone git://github.com/ninuxorg/nodeshot.git mapserver
    virtualenv mapserver
    cd mapserver
    source bin/activate
    pip install -r requirements.txt
    cp settings.example.py settings.py
    export DJANGO_SETTINGS_MODULE=settings
    ./manage.py syncdb && ./manage.py collectstatic && ./manage.py runserver

Enjoy on http://localhost:8000/ !
Admin site is at http://localhost:8000/admin/

PRODUCTION INSTALLATION
---------------
To install for production you'll need to install the python connectors for your database of choice (mysql-python or postgres_psycopg2), setup a virtual host in your web server and bind it to mod_wsgi.

For a complete installation guide please refer to installation guide
available here:
http://wiki.ninux.org/InstallNodeshot

QUESTIONS, CONTRIBUTIONS, DISCUSSION 
---------------
If you like this software and you are interested in contributing or you want to ask any question join our mailing list:
http://ml.ninux.org/mailman/listinfo/nodeshot

