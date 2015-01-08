**************
User Interface
**************

``nodeshot.ui.default`` is the default web user interface of nodeshot.

The default interface is replaceable: if you need a radically different web
interface you can develop a new one in a separate python package.

==================
Available settings
==================

``nodeshot.ui.default`` is enabled by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

These are the available customizable settings:

 * ``NODESHOT_UI_VOTING_ENABLED``
 * ``NODESHOT_UI_RATING_ENABLED``
 * ``NODESHOT_UI_COMMENTS_ENABLED``
 * ``NODESHOT_UI_ADDRESS_SEARCH_TRIGGERS``

NODESHOT_UI_VOTING_ENABLED
--------------------------

**default**: ``True``

Indicates wheter it is possible to like or dislike nodes.

NODESHOT_UI_RATING_ENABLED
--------------------------

**default**: ``True``

Indicates wheter it is possible to rate nodes (stars).

NODESHOT_UI_COMMENTS_ENABLED
----------------------------

**default**: ``True``

Indicates wheter it is possible to leave comments on nodes.

NODESHOT_UI_DISABLE_CLUSTERING_AT_ZOOM
--------------------------------------

**default**: ``12``

At the specified level of zoom clustering of points on the map is disabled.

Setting ``1`` disables clustering altogether, while setting ``0`` forces clustering at all zoom levels.

NODESHOT_UI_MAX_CLUSTER_RADIUS
------------------------------

**default**: ``90``

The maximum radius that a cluster will cover from the central marker (in pixels). Decreasing will make smaller clusters.

Setting ``1`` disables clustering altogether, while setting ``0`` forces clustering at all zoom levels.

NODESHOT_UI_DATETIME_FORMAT
---------------------------

**default**: ``dd MMMM yyyy, HH:mm``

``DateTime`` formatting according to the `jQuery dateFormat docs`_.

.. _jQuery dateFormat docs: https://github.com/phstc/jquery-dateFormat#date-and-time-patterns

NODESHOT_UI_DATE_FORMAT
-----------------------

**default**: ``dd MMMM yyyy``

``Date`` formatting according to the `jQuery dateFormat docs`_.

.. _jQuery dateFormat docs: https://github.com/phstc/jquery-dateFormat#date-and-time-patterns

NODESHOT_UI_ADDRESS_SEARCH_TRIGGERS
-----------------------------------

**default**:

.. code-block:: python

    [
        ',',
        'st.',
        ' street',
        ' square',
        ' road',
        'via ',
        'viale ',
        'piazza ',
        'strada ',
        'plaza',
        'calle '
    ]

Special strings that trigger geolocation when searching in the address bar.
