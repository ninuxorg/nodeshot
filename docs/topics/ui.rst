**************
User Interface
**************

``nodeshot.ui.default`` is the default web user interface of nodeshot.

The default interface is replaceable: if you need a radically different web
interface you can develop a new one in a separate python package.

=====================
Change the first page
=====================

By default the first page opened in the UI is a cms page called "home" which you can customize in the admin site under ``/admin/cms/page/1/``.

In this page you can put any HTML you want: images, graphs, whatever you think it's most suited to explain what your nodeshot instance does to first time visitors.

If you think you don't need this and you prefer to have a different index page, like for example the map view, just go to
``/admin/cms/menuitem/``, and change the order of the pages so that the first page you prefer comes first.

You might also unpublish or delete the links you don't want others to see, as well as add new links to the menu.

==================
Available settings
==================

``nodeshot.ui.default`` is enabled by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

These are the available customizable settings:

 * ``LEAFLET_CONFIG``
 * ``NODESHOT_UI_LEAFLET_OPTIONS``
 * ``NODESHOT_UI_DISABLE_CLUSTERING_AT_ZOOM``
 * ``NODESHOT_UI_MAX_CLUSTER_RADIUS``
 * ``NODESHOT_UI_DATETIME_FORMAT``
 * ``NODESHOT_UI_DATE_FORMAT``
 * ``NODESHOT_UI_ADDRESS_SEARCH_TRIGGERS``
 * ``NODESHOT_UI_LOGO``
 * ``NODESHOT_UI_VOTING_ENABLED``
 * ``NODESHOT_UI_RATING_ENABLED``
 * ``NODESHOT_UI_COMMENTS_ENABLED``
 * ``NODESHOT_UI_GOOGLE_ANALYTICS_UA``
 * ``NODESHOT_UI_GOOGLE_ANALYTICS_OPTIONS``
 * ``NODESHOT_UI_PIWIK_ANALYTICS_BASE_URL``
 * ``NODESHOT_UI_PIWIK_ANALYTICS_SITE_ID``
 * ``NODESHOT_UI_PRIVACY_POLICY_LINK``
 * ``NODESHOT_UI_TERMS_OF_SERVICE_LINK``

LEAFLET_CONFIG
--------------

**default**:

.. code-block:: python

    {
        'DEFAULT_CENTER': (49.06775, 30.62011),
        'DEFAULT_ZOOM': 4,
        'MIN_ZOOM': 1,
        'MAX_ZOOM': 18,
        'TILES': [
            ('Map', 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', '&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors | Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> &nbsp;<img src="https://developer.mapquest.com/content/osm/mq_logo.png">'),
            ('Satellite', 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Source: <a href="http://www.esri.com/">Esri</a> &copy; and the GIS User Community ')
        ],
    }

General options of the map:

* ``DEFAULT_CENTER``: default center of the map
* ``DEFAULT_ZOOM``: default zoom of the map
* ``MIN_ZOOM``: minimum zoom level
* ``MAX_ZOOM``: maximum zoom level
* ``TILES``: base layers available (eg: map, satellite), learn how to tweak this on the `django-leaflet documentation`_

.. _django-leaflet documentation: https://github.com/makinacorpus/django-leaflet#default-tiles-layer

NODESHOT_UI_LEAFLET_OPTIONS
---------------------------

**default**:

.. code-block:: python

    {
        'fillOpacity': 0.7,
        'opacity': 1,
        'dashArray': None,
        'lineCap': None,
        'lineJoin': None,
        'radius': 6,
        'temporaryOpacity': 0.3
    }

These options control some details of the map:

 * ``fillOpacity``: fill color opacity of objects on the map
 * ``opacity``: stroke opacity of objects on the map
 * ``dashArray``: explained in the `Leaflet documentation`_
 * ``lineCap``: explained in the `Leaflet documentation`_
 * ``lineJoin``: explained in the `Leaflet documentation`_
 * ``radius``: width of the radius circles on the map in pixel, valid only for points (*Nodeshot can display also other shapes*)
 * ``temporaryOpacity``: when adding a new node the other nodes are dimmed according to this option

Other options like fill color and stroke width are managed in the admin site under ``/admin/nodes/status/`` because they vary for each status.

.. _Leaflet documentation: http://leafletjs.com/reference.html#path

NODESHOT_UI_DISABLE_CLUSTERING_AT_ZOOM
--------------------------------------

**default**: ``12``

At the specified level of zoom clustering of points on the map is disabled.

Setting ``1`` disables clustering altogether, while setting ``0`` forces clustering at all zoom levels.

NODESHOT_UI_MAX_CLUSTER_RADIUS
------------------------------

**default**: ``90``

The maximum radius that a cluster will cover from the central marker (in pixels). Decreasing will make smaller clusters.

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
        ' avenue',
        ' lane',
        'footpath',
        'via ',
        'viale ',
        'piazza ',
        'strada ',
        'borgo ',
        'contrada ',
        'zona ',
        'fondo ',
        'vico ',
        'sentiero ',
        'plaza ',
        ' plaza',
        'calle ',
        'carrer ',
        'avenida '
    ]

Special strings that trigger geolocation when searching in the general search bar.

NODESHOT_UI_LOGO
----------------

**default**: ``None``

Use this setting to show a custom logo, example:

.. code-block:: python

    NODESHOT_UI_LOGO = {
        'URL': 'http://yourdomain.com/static/logo.svg',  # value for css rule background-image
        'SIZE': '180px',  # value for css rule background-size
    }

.. note::
    * the logo **must be in SVG format**.
    * when choosing the size of the logo, mind mobile platforms!

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

NODESHOT_UI_CONTACTING_ENABLED
------------------------------

**default**: ``True``

Indicates wheter it is possible to contact other users.

NODESHOT_UI_GOOGLE_ANALYTICS_UA
-------------------------------

**default**: ``None``

Google Analytics tracking code.

Example:

.. code-block:: python

    NODESHOT_UI_GOOGLE_ANALYTICS_UA = 'UA-XXXXXXXX-3'

NODESHOT_UI_GOOGLE_ANALYTICS_OPTIONS
------------------------------------

**default**: ``auto``

Google Analytics options that will be passed on initialization.

.. code-block:: python

    NODESHOT_UI_GOOGLE_ANALYTICS_OPTIONS = {
        'cookieDomain': 'none'
    }

For more information about the options that can be passed see the relative `Google Analytics Reference`_.

.. _Google Analytics Reference: https://developers.google.com/analytics/devguides/collection/analyticsjs/advanced#customizeTracker

NODESHOT_UI_PIWIK_ANALYTICS_BASE_URL
------------------------------------

**default**: ``None``

Piwik is a fantastic `Open Source Web Analytics`_ tool.

This settings indicates where you installed your own piwik instance.

Example:

.. code-block:: python

    NODESHOT_UI_PIWIK_ANALYTICS_BASE_URL = 'http://analytics.frm.ninux.org'

.. _Open Source Web Analytics: http://piwik.org/

NODESHOT_UI_PIWIK_ANALYTICS_SITE_ID
-----------------------------------

**default**: ``None``

Piwik site id.

Example:

.. code-block:: python

    NODESHOT_UI_PIWIK_ANALYTICS_SITE_ID = 12

NODESHOT_UI_PRIVACY_POLICY_LINK
-------------------------------

**default**: ``'#/pages/privacy-policy'``

Link to "Privacy Policy" page.

NODESHOT_UI_TERMS_OF_SERVICE_LINK
---------------------------------

**default**: ``'#/pages/terms-of-service'``

Link to "Terms of Service" page.
