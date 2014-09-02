****************
Interoperability
****************

Nodeshot has a built mechanism named "interoperability", which is basically an
abstraction layer between nodeshot and other third party applications which have
similarities in common (georeferenced data).

There are mainly four strategies through which we can achieve interoperability:

 * **periodic synchronization**: data is synchronized periodically with a background job
 * **event driven synchronization**: add, change, delete
 * **a mix of the two**: periodic and event driven
 * **RESTful translator**: nodeshot gets data on the fly and converts the format

These strategies are implemented through some Python classes called **"Synchronizers"**.

New synchronizers can be written ad hoc for each application that need to be supported.

=====================
Internal dependencies
=====================

For the **interoperability** module to work, the following apps must be listed in ``settings.INSTALLED_APPS``:

 * nodeshot.core.layers
 * nodeshot.core.nodes
 * nodeshot.interoperability

=================
Required settings
=================

the module ``nodeshot.interoperability`` needs to be in ``settings.INSTALLED_APPS``::

    INSTALLED_APPS = [
        # dependencies
        'nodeshot.core.layers',
        'nodeshot.core.nodes',
        # interoperabiliy module
        'nodeshot.interoperability',
        # ...
    ]

the celery beat settings must be uncommented (you might want to tweak how often
data is synchronized, default is 12 hours)::

    from datetime import timedelta

    CELERYBEAT_SCHEDULE = {
        'synchronize': {
            'task': 'nodeshot.interoperability.tasks.synchronize_external_layers',
            'schedule': timedelta(hours=12),
        },
        # other tasks
    }

=================
Configure a layer
=================

Interoperability is configured at layer level in the admin interface.

A layer must be flagged as **"external"** and can be configured by editing the
field **config**, which is a JSON representation of the configuration keys.

===================
Synchronize command
===================

When developing you can use the django management command "synchronize", which
can be used in several different ways, see the help output::

    python manage.py synchronize --help

**Sync one layer**::

    python manage.py synchronize layer-slug

**Sync multiple layers** by specifying space separated layer slugs::

    python manage.py synchronize layer1-slug layer2-slug

**Sync all layers** is as simple as that::

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

Save the synchronizer in your python path, name it exactly as you named the class,
in our example that would be ``MyVeryCoolApp.py``:

Once the file is saved and you are sure it's on your pythonpath you have to add a
tuple in ``settings.NODESHOT_SYNCHRONIZERS`` in which the first element is the path to the file and
the second element is the name you want to show in the admin interface in the list *"synchronizer_class"*:

.. code-block:: python

    NODESHOT_SYNCHRONIZERS = [
        ('myproject.synchronizers.MyVeryCoolApp', 'MyVeryCoolApp'),
    ]

This will add your new synchronizer to the default list.
