*****
Nodes
*****

``nodeshot.core.nodes`` is the core geographic app of nodeshot.

Nodes have the following features:

 * geometry can be a ``Point``, a ``Polygon`` or a ``Linestring``
 * have to belong to a ``Layer`` if ``nodeshot.core.layers`` is enabled (which it is by default)
 * have a status, which can be customized in the admin, by default statuses are **potential**, **active**, **planned**
 * have other properties like **description**, **address**, ecc.
 * can have custom properties by leveraging the ``NODESHOT_NODES_HSTORE_SCHEMA`` setting

Other modules extend the Node object and add several functionalities like comments, votes, ecc.

**Additional features**:

 * Possibility to customize the default node schema by adding custom fields
 * Set the default status of nodes from admin
 * Nodes can be published by default or not
 * Nodes may store descriptions in HTML format
 * Elevation API, a proxy to Google Elevation API, default URL is at ``/api/v1/elevation/``

==================
Available settings
==================

``nodeshot.core.nodes`` is enabled by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

These are the available customizable settings:

 * ``NODESHOT_NODES_HSTORE_SCHEMA``
 * ``NODESHOT_NODES_PUBLISHED_DEFAULT``
 * ``NODESHOT_NODES_REVERSION_ENABLED``
 * ``NODESHOT_NODES_HTML_DESCRIPTION``
 * ``NODESHOT_GOOGLE_ELEVATION_API_KEY``
 * ``NODESHOT_GOOGLE_ELEVATION_DEFAULT_SAMPLING``

NODESHOT_NODES_HSTORE_SCHEMA
----------------------------

**default**: ``None``

``NODESHOT_NODES_HSTORE_SCHEMA``: custom **django-hstore** schema to add new fields on the ``Node`` model and API.

The following example will add a choice field with a select of 3 choices:

.. code-block:: python

    # settings.py

    NODESHOT_NODES_HSTORE_SCHEMA = [
        {
            'name': 'choice',
            'class': 'CharField',
            'kwargs': {
                'max_length': 128,
                'choices': [
                    ('choice1', 'Choice 1'),
                    ('choice2', 'Choice 2'),
                    ('choice3', 'Choice 3')
                ],
                'default': 'choice1'
            }
        }
    ]

Consult the `django-hstore documentation`_ for more information (look for ``schema mode``).

.. _django-hstore documentation: http://djangonauts.github.io/django-hstore/#_model_setup

NODESHOT_NODES_PUBLISHED_DEFAULT
--------------------------------

**default**: ``True``

Whether the default value for the **"is_published"** field on new nodes will be ``True`` or ``False``.

Use ``False`` if you want new nodes to be reviewed by an admin before showing publicly on the site.

NODESHOT_NODES_REVERSION_ENABLED
--------------------------------

**default**: ``True``

Indicates whether the ``Node`` model can revert changes saved in the history by using `django-reversion`_.

.. _django-reversion: https://github.com/etianen/django-reversion

NODESHOT_NODES_HTML_DESCRIPTION
-------------------------------

**default**: ``True``

Indicates whether the **"description"** field of the ``Node`` model allows **HTML** or not.

If ``True`` an **WYSIWYG** editor will be used in the admin site.

NODESHOT_GOOGLE_ELEVATION_API_KEY
---------------------------------

**default**: ``None``

API key of the `Google Elevation API`_.

This setting is optional, but registering an API key is recommended by Google.

See the `Google Elevation API`_ documentation for more information.

.. _Google Elevation API: https://developers.google.com/maps/documentation/elevation/

NODESHOT_GOOGLE_ELEVATION_DEFAULT_SAMPLING
------------------------------------------

**default**: ``50``

.. warning::
    Setting a very low value may cause the reach of the usage limits of the Google Elevation API.

Calculates automatic sampling to get one point every ``x`` meters, where ``x`` is
the value specified in ``NODESHOT_GOOGLE_ELEVATION_DEFAULT_SAMPLING``.

**A bit more explaination is needed**: when sending sampled path requests to the `Google Elevation API`_
a ``samples`` parameter is required:

.. note::
    ``samples`` *(required)* specifies the number of sample points along a path for which to return elevation data.
    The samples parameter divides the given path into an ordered set of equidistant points along the path.

If no ``samples`` parameter is specified in the HTTP request to the elevation API resource, nodeshot will take care of it automatically,
ensuring there are enough points to represent a meaningful elevation profile.

The default value is **50 meters**, which will return 20 sample points for each kilometer.
