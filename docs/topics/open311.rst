=========================
Open 311 API
=========================

Nodeshot comes with a self-documented API, in order to insert nodes, comments,
votes or ratings as service requests, according to the Open 311 standard (http://open311.org/).

---------------
Settings
---------------
The modules ``nodeshot.layers`` , ``nodeshot.nodes`` , ``nodeshot.participation``
and ``nodeshot.open311`` need to be in ``settings.INSTALLED_APPS``::

    INSTALLED_APPS = [
        # dependencies
        'nodeshot.community.participation'
        'nodeshot.core.layers',
        'nodeshot.core.nodes',
        # Open 311 module
        'nodeshot.open311',
        # ...
    ]

Specific settings for Open 311 are configured in NODESHOT['OPEN311'] inside ``settings.py``::

    'OPEN311': {
        #Metadata for service discovery
        'DISCOVERY': {
            'changeset':'2014-02-03 14:18',
            'contact':'email or phone number for assistance',
            'key_service':'URL for api_key requests',
            'endpoints':[
              {
                'specification':'http://wiki.open311.org/GeoReport_v2',
                'url':'Public URL of your endpoint',
                'changeset':'2014-02-03 09:01',
                'type':'production',
                'formats':[
                  'application/json'
                ]
              },
              
            ]
          },
        # Do not change this unless you want to redefine Open311 service definitions
        'METADATA': 'true',
        'TYPE': 'realtime',
        # Change the following, according to the statuses you have configured the admin
        'STATUS' : {
            'potential': 'open',
            'planned': 'open',
            'active': 'closed',
        }
    }

'DISCOVERY' is a dictionary containing service discovery metadata. Inside it, you
can define different endpoints (e.g production, test, development, ecc..)

See http://wiki.open311.org/Service_Discovery for more details.

'METADATA' and 'TYPE' need to be changed only in order to completely redefine the
implementation of Nodeshot Open 311 service definition.

See http://wiki.open311.org/GeoReport_v2 for details but you probably don't want to do this!

'STATUS' is a dictionary, containing the values that have been inserted in 'Status'
model as keys, and 'open' or 'closed' as possible values. It is important that the
keys of this dictionary exactly match the values of the slug fields contained in
the STATUS records, otherwise the application will either throw an exception
(if in DEBUG mode) or defaults to "closed" (production).

In its simpliest form, the configuration would be this::

    'STATUS' : {
            'Open' : 'open',
            'Closed' : 'closed',
        }
Or, if more statuses are possible in your configuration, like in the example below:

.. image:: statuses.png

each status can be mapped to one of the two values 'open' or 'closed', depending on your needs::

    'STATUS' : {
            'Potential' : 'open',
            'Planned' : 'open',
            'Active' : 'closed',
        }