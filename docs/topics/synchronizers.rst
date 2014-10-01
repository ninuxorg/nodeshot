*************
Synchronizers
*************

``nodeshot.interop.sync`` is a django-app that enables nodeshot to build an
abstraction layer between itself and other third party web-applications which deal with georeferenced data.

There are mainly four strategies through which we can achieve interoperability with third party web apps:

 * **periodic synchronization**: data is imported periodically into the local database by a background job which reads an external source
 * **event driven synchronization**: data is exported to a third party API whenever local data is added, changed or deleted
 * **RESTful translator**: data is retrieved on the fly and converted to json/geojson, no data is saved in the database
 * **mixed**: custom synchronizers might implement mixed strategies

These strategies are implemented through **"Synchronizers"**.

New synchronizers can be written ad-hoc for each application that need to be supported.

=====================
Internal dependencies
=====================

To enable this feature, the following apps must be listed in ``settings.INSTALLED_APPS``:

 * nodeshot.core.layers
 * nodeshot.core.nodes
 * nodeshot.interop.sync

By default these three apps are installed.

=================
Required settings
=================

The module ``nodeshot.interop.sync`` is activated by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

For periodic synchronization ``CELERYBEAT_SCHEDULE`` must be uncommented in your ``settings.py``::

    from datetime import timedelta

    CELERYBEAT_SCHEDULE.update({
        'synchronize': {
            'task': 'nodeshot.interop.sync.tasks.synchronize_external_layers',
            'schedule': timedelta(hours=12),
        },
        # ... other tasks ...
    })

You might want to tweak how often data is synchronized, in the previous example we configured the task to run every 12 hours.

===================
Layer configuration
===================

Interoperability is configured at layer level in the admin interface.

A layer must be flagged as **"external"**, after doing so a new box labeled "External layer info"
will appear in the bottom of the page. If the layer is new and not saved in the database proceed to save and reload the admin page.

Then change the synchronizer field and the configuration fields will appear.

Each synchronizer has different fields, an brief explaination of the default synchronizers follows.

Nodeshot (RESTful translator)
-----------------------------

This synchronizer is a **RESTful translator** and allows to reference the nodes of an external nodeshot instance.

There are two required configuration keys:

 * **layer url**: URL of the layer API resource, eg: ``https://test.map.ninux.org/api/v1/layers/rome/``
 * **verify ssl**: indicates wether the SSL certificate of the external layer should be verified or not; if checked self signed certificates won't work

There is no periodic synchronization needed because this synchronizer grabs the data on the fly.

GeoJSON (periodic sync)
-----------------------

This synchronizer implements the **periodic synchronization** strategy and therefore needs to be enabled
in the ``CELERYBEAT_SCHEDULE`` setting.

The main configuration keys are:

 * **url**: URL to retrieve the geojson file
 * **verify_ssl**: indicates wether the SSL certificate of the external layer should be verified or not; if checked self signed certificates won't work
 * **default status**: status to be used for new nodes, to use the system default leave blank

There are other configuration keys which enable to parse geojson files which use radically different names for corresponding fields.

 * **name**: corresponding name field, for example, on the data source file the name field could be labeled **title**
 * **status**: corresponding status field, if present
 * **description**: corresponding description field, if present
 * **address**: corresponding address field, if present
 * **is_published**: corresponding is_published field, if present
 * **user**: corresponding user field, if present
 * **elev**: corresponding elev field, if present
 * **notes**: corresponding notes field, if present
 * **added**: corresponding added field, if present
 * **updated**: corresponding updated field, if present

GeoRSS (periodic sync)
----------------------

This synchronizer implements the **periodic synchronization** strategy and therefore needs to be enabled
in the ``CELERYBEAT_SCHEDULE`` setting.

The main configuration keys are:

 * **url**: URL to retrieve the georss file
 * **verify_ssl**: indicates wether the SSL certificate of the external layer should be verified or not; if checked self signed certificates won't work
 * **default status**: status to be used for new nodes, to use the system default leave blank

There are other configuration keys which enable to parse georss files which use radically different names for corresponding fields.

 * **name**: corresponding name field, defaults to **title**
 * **status**: corresponding status field, if present
 * **description**: corresponding description field, if present
 * **address**: corresponding address field, if present
 * **is_published**: corresponding is_published field, if present
 * **user**: corresponding user field, if present
 * **elev**: corresponding elev field, if present
 * **notes**: corresponding notes field, if present
 * **added**: corresponding added field, defaults to **pubDate**
 * **updated**: corresponding updated field, if present

OpenWisp (periodic sync)
------------------------

This synchronizer inherits from the **GeoRSS** synchronizer, the available options and configurations are the same.

The only difference is that this synchronizer is designed to grab data from the GeoRSS file produced by `OpenWISP Geographic Monitoring`_.

.. _OpenWISP Geographic Monitoring: https://github.com/openwisp/OpenWISP-Geographic-Monitoring

=======================
Sync management command
=======================

This is the command which is used to perform **periodic synchronization**, use ``--help`` to know its options::

    python manage.py sync --help

**Sync a specific layer**::

    python manage.py sync layer-slug

**Sync multiple layers** by specifying space separated layer slugs::

    python manage.py sync layer1-slug layer2-slug

**Sync all layers** is as simple as::

    python manage.py sync

**Sync all layers except those specified in --exclude**::

    python manage.py sync --exclude=layer1-slug,layer2-slug

    # spaces are allowed as long as string is wrapped in quotes/doublequotes

    python manage.py sync --exclude="layer1-slug, layer2-slug"

=========================
Writing new synchronizers
=========================

To write new synchronizers, you should extend the class ``GenericGisSynchronizer``
in ``/nodeshot/interoperability/synchronizers/base.py``:

.. code-block:: python

    # my_very_cool_app.py

    from nodeshot.interop.sync.synchronizer.base import GenericGisSynchronizer

    class MyVeryCoolApp(GenericGisSynchronizer):
        """ Synchronizer for my MyVeryCoolApp """
        pass

.. note::
    this section is a work in progress.

Once the file is saved and you are sure it's on your pythonpath you have to add a
tuple in ``settings.NODESHOT_SYNCHRONIZERS`` in which the first element is the path to the file and
the second element is the name you want to show in the admin interface in the *"Synchronizer"* select:

.. code-block:: python

    NODESHOT_SYNCHRONIZERS = [
        ('myproject.synchronizers.my_very_cool_app.MyVeryCoolApp', 'MyVeryCoolApp'),
    ]

This will add your new synchronizer to the default list.

====================
Third party packages
====================

 * nodeshot-citysdk-synchronizers: https://github.com/nemesisdesign/nodeshot-citysdk-synchronizers
