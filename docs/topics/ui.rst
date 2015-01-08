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
--------------------------

**default**: ``True``

Indicates wheter it is possible to leave comments on nodes.

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
