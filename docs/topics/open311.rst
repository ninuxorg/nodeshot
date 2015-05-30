.. _open311-label:
***********
Open311 API
***********

Nodeshot comes with a self-documented open311 API, in order to insert nodes, comments,
votes or ratings as service requests, according to the Open 311 specification (http://open311.org/).

This app depends on the **participation** app, be sure to read its :ref:`documentation <participation-label>`.

========
Settings
========

``nodeshot.interop.open311`` and its dependencies are enabled by deafult.

In case you want to disable this app consult the **"Uninstall"** section below.

The available settings for the Open311 app are the following:

 * ``NODESHOT_OPEN311_DISCOVERY``
 * ``NODESHOT_OPEN311_METADATA``
 * ``NODESHOT_OPEN311_TYPE``
 * ``NODESHOT_OPEN311_STATUS``

``NODESHOT_OPEN311_DISCOVERY`` is a dictionary containing service discovery metadata. Inside it, you
can define different endpoints (e.g production, test, development, ecc..)

See http://wiki.open311.org/Service_Discovery for more details.

``NODESHOT_OPEN311_METADATA`` and ``NODESHOT_OPEN311_TYPE`` need to be changed only in order to completely redefine the
implementation of Nodeshot Open 311 service definition.

See http://wiki.open311.org/GeoReport_v2 for details but you probably don't want to do this!

``NODESHOT_OPEN311_STATUS`` is a dictionary, containing the values that have been inserted in 'Status'
model as keys, and 'open' or 'closed' as possible values. It is important that the
keys of this dictionary match exactly the values of the slug fields contained in
the Status model records, otherwise the application will either throw an exception
(if in DEBUG mode) or defaults to "closed" (production).

In its simpliest form, the configuration would be this::

    'STATUS' : {
        'open' : 'open',
        'closed' : 'closed',
    }

Or, if more statuses are possible in your configuration, like in the example below:

.. figure:: images/statuses.png

each status can be mapped to one of the two values 'open' or 'closed', depending on your needs::

    'STATUS' : {
        'potential' : 'open',
        'planned' : 'open',
        'active' : 'closed'
    }

=========
Uninstall
=========

To uninstall ``nodeshot.interop.open311`` simply remove it from your ``settings.INSTALLED_APPS``

.. code-block:: python

    # setings.py

    # import the default nodeshot settings
    # do not move this import
    from nodeshot.conf.settings import *

    # ------ All settings customizations must go here ------ #

    INSTALLED_APPS.remove('nodeshot.interop.open311')
