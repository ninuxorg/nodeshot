****************
Interoperability
****************

Nodeshot has a built mechanism named "interoperability", which is basically an
abstraction layer between nodeshot and other third party applications which have
similarities in common (georeferenced data).

There are mainly four strategies through which we can achieve interoperability:

 * **periodic synchronization**: data is synchronized periodically (which means it is saved in the database) by a background job
 * **event driven synchronization**: data is synchronized whenever local data is added, changed or deleted
 * **RESTful translator**: data is retrieved on the fly and converted to json/geojson, no data is saved in the database
 * **mixed**: custom synchronizers might implement a mixed behaviour

These strategies are implemented through **"Synchronizers"**.

New synchronizers can be written ad-hoc for each application that need to be supported.

=====================
Internal dependencies
=====================

For the **interoperability** module to work, the following apps must be listed in ``settings.INSTALLED_APPS``:

 * nodeshot.core.layers
 * nodeshot.core.nodes
 * nodeshot.interoperability

By default these three apps are installed.

=================
Required settings
=================

The module ``nodeshot.interoperability`` is activated by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

For periodic synchronization ``CELERYBEAT_SCHEDULE`` must be uncommented in your ``settings.py``::

    from datetime import timedelta

    CELERYBEAT_SCHEDULE.update({
        'synchronize': {
            'task': 'nodeshot.interoperability.tasks.synchronize_external_layers',
            'schedule': timedelta(hours=12),
        },
        # ... other tasks ...
    })

You might want to tweak how often data is synchronized, in the previous example we configured the task to run every 12 hours.

===================
Layer configuration
===================

Interoperability is configured at layer level in the admin interface.

A layer must be flagged as **"external"** and can be configured by editing the
field **config**, which is a JSON representation of the configuration keys.

Each synchronizer has different required configuration keys.

Nodeshot synchronizer
---------------------

This synchronizer is a **RESTful translator** and allows to reference the nodes of an external nodeshot instance.

There are two required configuration keys:

 * ``layer_url`` (string): URL of the layer API resource, eg: ``https://test.map.ninux.org/api/v1/layers/rome/``
 * ``verify_ssl`` (boolean): indicates wether the SSL certificate of the external layer should be verified or not; if set to ``true`` self signed certificates won't work

 There is no periodic synchronization needed because this synchronizer grabs the data on the fly.

===================
Synchronize command
===================

This is the command which is used to perform **periodic synchronization**, use ``--help`` to know its options::

    python manage.py synchronize --help

**Sync a specific layer**::

    python manage.py synchronize layer-slug

**Sync multiple layers** by specifying space separated layer slugs::

    python manage.py synchronize layer1-slug layer2-slug

**Sync all layers** is as simple as::

    python manage.py synchronize

**Sync all layers except those specified in --exclude**::

    python manage.py synchronize --exclude=layer1-slug,layer2-slug

    # spaces are allowed as long as string is wrapped in quotes/doublequotes

    python manage.py synchronize --exclude="layer1-slug, layer2-slug"

=========================
Writing new synchronizers
=========================

To write new synchronizers, you should extend the class ``GenericGisSynchronizer``
in ``/nodeshot/interoperability/synchronizers/base.py``:

.. code-block:: python

    from nodeshot.interoperability.synchronizer.base import GenericGisSynchronizer

    class MyVeryCoolApp(GenericGisSynchronizer):
        """ Synchronizer for my MyVeryCoolApp """
        pass

.. note::
    this section is a work in progress.

Once the file is saved and you are sure it's on your pythonpath you have to add a
tuple in ``settings.NODESHOT_SYNCHRONIZERS`` in which the first element is the path to the file and
the second element is the name you want to show in the admin interface in the list *"synchronizer_class"*:

.. code-block:: python

    NODESHOT_SYNCHRONIZERS = [
        ('myproject.synchronizers.my_very_cool_app.MyVeryCoolApp', 'MyVeryCoolApp'),
    ]

This will add your new synchronizer to the default list.
