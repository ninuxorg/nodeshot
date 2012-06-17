                 _           _           _   
 _ __   ___   __| | ___  ___| |__   ___ | |_ 
| '_ \ / _ \ / _` |/ _ \/ __| '_ \ / _ \| __|
| | | | (_) | (_| |  __/\__ \ | | | (_) | |_ 
|_| |_|\___/ \__,_|\___||___/_| |_|\___/ \__|

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


INSTALLATION
---------------
For a complete installation guide please refer to installation guide
available here:
http://wiki.ninux.org/InstallNodeshot

To run some test just type:

    sudo pip install Django django-extensions
    git clone git://github.com/ninuxorg/nodeshot.git mapserver
    cd mapserver
    cp settings.example.py settings.py
    ./manage.py syncdb && ./manage.py runserver

Enjoy on http://localhost:8000 !


If you have any question, please feel free to contact us:
    contatti@ninux.org

