***************************
Self documented RESTful API
***************************

.. image:: nodeshot-api.png

Nodeshot provides a JSON RESTful API to manage most of the data in its database.

The API is **self-documented**, **browsable** and has two levels of documentation.

By default (according to ``NODESHOT['SETTINGS']['API_PREFIX']``) the API is reachable at **http://localhost:8000/api/v1/**.

Replace *http://localhost:8000* with your actual hostname.

========
Settings
========

The API is enabled by default in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        
        # nodeshot
        'nodeshot.core.api',
        
        # ...
    ]
    
    # ...
    
    NODESHOT = {
        
        'SETTINGS': {
            # api prefix examples:
            #   * api/
            #   * api/v1/
            # leave blank to include api urls at root level, such as /nodes/, /layers/ and so on
            'API_PREFIX': 'api/v1/',
            # other settings ...
        },
        
        # other settings ...
        
        'API': {
            'APPS_ENABLED': [
                'nodeshot.core.nodes',
                'nodeshot.core.layers',
                'nodeshot.core.cms',
                'nodeshot.community.profiles',
                'nodeshot.community.participation',
                'nodeshot.community.notifications',
                'nodeshot.community.mailing',
                'nodeshot.networking.net',
                'nodeshot.networking.links',
                'nodeshot.networking.services'
            ]
        },
        
        # other settings ...
    }

=================
API Documentation
=================

By default when you open the API you will see the **self-documented** HTML version.

.. image:: API-resource.png

Each resource has a general description of what is its purpose and which operations supports.

The resources which perform write operations will also have an HTML form with which you can experiment and test the API.

.. image:: API-form.png

There's also another auto generated documentation that makes use of the standard **swagger** format which you can see at **http://localhost:8000/api/v1/docs/**

.. image:: swagger.png