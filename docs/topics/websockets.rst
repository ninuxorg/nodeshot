***********
Web Sockets
***********

Web Sockets in nodeshot are implemented through an experimental django app in
``nodeshot.core.websockets``.

**This app will be removed in favour of a better functioning module soon.**

--------------
How to disable
--------------

If you need to disable this feature altogether add this at the bottom of your ``settings.py``:

.. code-block:: python

    INSTALLED_APPS.remove('nodeshot.core.websockets')
