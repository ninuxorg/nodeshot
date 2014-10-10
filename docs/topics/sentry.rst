******************
Sentry integration
******************

Nodeshot can be monitored by `sentry`_ pretty easily.

All you have to do is to set your sentry API key (also known as DSN URL) in your ``settings.py``. Look for ``RAVEN_CONFIG``:

.. code-block:: python

    # settings.py

    # sentry integration
    RAVEN_CONFIG = {
       'dsn': 'https://<api-public-key>:<api-secret-key>@<sentry.host>/<id>?timeout=5&verify_ssl=0',
    }

After this change remember to reload the **uwsgi** application server::

    supervisorctl restart uwsgi


.. _sentry: https://getsentry.com/welcome/
