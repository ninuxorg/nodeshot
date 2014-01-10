*******************************
Import data from older versions
*******************************

The new version provides an integrated tool that allows to import data from older nodeshot versions (0.9.x).

.. warning::
    this tool is a work in progress, please report any bug in our `Mailing List`_.

.. _Mailing List: http://ml.ninux.org/mailman/listinfo/nodeshot.

=====================
Internal dependencies
=====================

For the **oldimporter** module to work, the following apps must be listed in ``settings.INSTALLED_APPS``:

 * nodeshot.core.nodes
 * nodeshot.core.layers
 * nodeshot.networking.net
 * nodeshot.networking.links
 * nodeshot.community.mailing
 * nodeshot.community.profiles

===========
Preparation
===========

Due to some major differences between the old and the new version some manual preparation needs to be done.

------------------------------------
0. Ensure your database is reachable
------------------------------------

In order for the **oldimporter** to work it musts be able to connect to the remote old database.

If your old database is MySQL or PostgreSQL you should tweak its configuration to
allow connections from the IP/hostname where the new version of nodeshot is installed.

If your old database is Sqlite you can just copy the file to the new machine.

------------------------
1. Create Status Objects
------------------------

First of all, if you were using the old nodeshot version we assume that you are
using nodeshot for a community network or a wifi network.

So you must create the status objects which are appropiate for a community network.

Start with the basic ones and then after the imports you might change their names, order, or whatever.

So laod the default status objects::

    cd /var/www/nodeshot/projects/ninux
    # activate virtual env
    source python/bin/activate
    
    python manage.py loaddata default_status

----------------
2. Create Layers
----------------

Then ensure you have some layers defined in your admin interface.
Open the browser and go to **/admin/layers/layer** (or follow the links from the admin index),
if you see any layer defined, you are ready to proceed, if not you should create one or more layers.

If you **specify the area of each layer**, the importer will be able to insert the
old nodes into the right layer. It's a good thing to do it!

If you don't want to lose any node, you should create a **default layer** in which
the script will automatically put all those old nodes which have coordinates that
are not comprised in any of your newly created layers.

**If no default layer is specified the nodes which have coordinates not comprised
in any layer will be discarded.**

=====================
Enable in settings.py
=====================

Uncomment the following section in ``settings.py`` and tweak the settings
``ENGINE``, ``NAME``, ``USER``, ``PASSWORD``, ``HOST`` and ``PORT``
according to your configuration, but leave ``DATABASE_ROUTERS`` unchanged:

.. code-block:: python

    if 'test' not in sys.argv:
        DATABASES['old_nodeshot'] = {
           'ENGINE': 'django.db.backends.mysql',  # might be also postgresql or sqlite
           'NAME': 'nodeshot',
           'USER': 'nodeshot-readonly',
           'PASSWORD': '*********',
           'HOST': 'remote-ip',
           'PORT': 'remote-port',
        }
        DATABASE_ROUTERS = [
            'nodeshot.extra.oldimporter.db.DefaultRouter',
            'nodeshot.extra.oldimporter.db.OldNodeshotRouter'
        ]

Uncomment ``nodeshot.extra.oldimporter`` in ``settings.INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # dependencies
        'nodeshot.core.nodes',
        'nodeshot.core.layers',
        'nodeshot.networking.net',
        'nodeshot.networking.links',
        'nodeshot.community.mailing',
        'nodeshot.community.profiles',
        
        # oldimporter module
        'nodeshot.extra.oldimporter',
        
        # ...
    ]

And set the ``DEFAULT_LAYER`` (object id/primary key):

.. code-block:: python

    # ...

    'OLD_IMPORTER':{
        'DEFAULT_LAYER': 1,
        'STATUS_MAPPING': {
            'a': 'active',
            'h': 'active',
            'ah': 'active',
            'p': 'potential',
            'default': 'potential'
        }
    },
    
    # ...

If you followed exactly the instructions in this document you can leave the default ``STATUS_MAPPING`` setting unchanged.

========================
Install database drivers
========================

Most production installations of old nodeshot versions used MySQL
(development quick install were done with SQlite).

Because these drivers are not installed by default with the default install procedure, you will have to install them now.

For MySQL you can do::

    sudo apt-get install libmysqlclient-dev
    
    cd /var/www/nodeshot/projects/ninux
    source python/bin/activate
    pip install MySQL-python

===========
Import data
===========

Ready? Go!::

    python manage.py import_old_nodeshot

Wait for the importer to import your data, when it finishes it will ask you if you
are satisfied with the results or not, if you enter "No" the importer will delete all
the imported records.

======================
Deactivate oldimporter
======================

When you are finished using the oldimporter module you can disable it by removing
it from ``settings.INSTALLED_APPS`` and by removing/commenting the
``DATABASES['old_nodeshot']`` setting.

===========================
How does the importer work?
===========================

Let's explain some technical details, the flow can be divided in 7 steps.

--------------------------
1. Retrieve all nodes
--------------------------

The first thing the script will do is to retrieve all the nodes from the old database
and convert the queryset in a python list that will be used in the next steps.

-------------------------------
2. Extract user data from nodes
-------------------------------
    
Since in old nodeshot there are no users but each node contains data
such as name, email, and stuff like that, the script will create user accounts:

 * loop over nodes and extract a list of unique emails
 * each unique email will be a new user in the new database
 * each new user will have a random password set
 * save users, email addresses

---------------
3. Import nodes
---------------
    
    * **USER**: assign owner (the link is the email)
    * **LAYER**: assign layer (layers must be created by hand first!):
        1. if node has coordinates comprised in a specified layer choose that
        2. if node has coordinates comprised in more than one layer prompt the user which one to choose
        3. if node does not have coordinates comprised in any layer:
            1. use default layer if specified (configured in settings)
            2. discard the node if no default layer specified
    * **STATUS**: assign status depending on configuration:
        ``settings.NODESHOT['OLD_IMPORTER']['STATUS_MAPPING']`` must be a dictionary in which the
        key is the old status value while the value is the new status value
        if ``settings.NODESHOT['OLD_IMPORTER']['STATUS_MAPPING']`` is False the default status will be used
    * **HOSTPOT**: if status is hotspot or active and hotspot add this info in *HSTORE* data field

-----------------
4. Import devices
-----------------

In this step the script will import devices and create any missing routing protocol.

-----------------------------------------
5. Import interfaces, ip addresses, vaps
-----------------------------------------

In this step the script will import all interfaces, ip addresses and other detailed device info.

----------------
6. Import links
----------------

In this step the script will import all the available links.

-------------------
7. Import Contacts
-------------------

In this step the script will import the contact logs.