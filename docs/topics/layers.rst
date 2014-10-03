******
Layers
******

``nodeshot.core.layers`` is a django-app that enables nodeshot to group nodes in layers.

A layer may have a geographic area and an organization in charge of it.

The **area** field is required and can be either a **polygon** or a **point**. If a polygon is used,
its nodes will have to be contained in it and its center will be calculated automatically;
otherwise, if a point is used its nodes will be allowed to be located anywhere and the point will be considered its center.

==================
Available settings
==================

``nodeshot.core.layers`` is enabled by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

These are the available customizable settings:

 * ``NODESHOT_LAYERS_HSTORE_SCHEMA``
 * ``NODESHOT_API_APPS_ENABLED``

NODESHOT_LAYERS_HSTORE_SCHEMA
-----------------------------

**default**: ``None``

custom **django-hstore** schema to add new fields on the ``Layer`` model and API.

The following example will add a category field with a select of 3 choices:

.. code-block:: python

    # settings.py

    NODESHOT_LAYERS_HSTORE_SCHEMA = [
        {
            'name': 'category',
            'class': 'CharField',
            'kwargs': {
                'max_length': 128,
                'choices': [
                    ('category1', 'Category 1'),
                    ('category2', 'Category 2'),
                    ('category3', 'Category 3')
                ],
                'default': 'category1'
            }
        }
    ]

Consult the `django-hstore documentation`_ for more information (look for ``schema mode``).

.. _django-hstore documentation: http://djangonauts.github.io/django-hstore/#_model_setup

NODESHOT_LAYERS_NODES_MINIMUM_DISTANCE
--------------------------------------

**default**: ``0``

Default value for the field ``nodes_minimum_distance`` on the ``Layer`` model.

NODESHOT_LAYERS_REVERSION_ENABLED
---------------------------------

**default**: ``True``

Indicates whether the Layer model can revert changes saved in the history by using `django-reversion`_.

.. _django-reversion: https://github.com/etianen/django-reversion

NODESHOT_LAYERS_TEXT_HTML
-------------------------

**default**: ``True``

Indicates whether the **"Extended text"** field of the ``Layer`` model allows **HTML** or not.

If ``True`` a **WYSIWYG** editor will be used in the admin site.
