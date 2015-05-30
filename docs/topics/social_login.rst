*************
Social Logins
*************

This section describes how to enable social logins for your instance.

========
Facebook
========

 1. Go to https://developers.facebook.com/
 2. Create an app, specify your website domain
 3. Grab **App ID** and **App Secret**
 4. Fill ``FACEBOOK_APP_ID`` in ``settings.py``
 5. Fill ``FACEBOOK_API_SECRET`` in ``settings.py``

=======
Google+
=======

 1. Go to https://code.google.com/apis/console#access to request a new API key
 2. Create an OAuth app
 3. Specify your website URL in ``AUTHORIZED JAVASCRIPT ORIGINS`` in Google's developer site
 4. Specify ``URL/complete/google-oauth2/`` in ``AUTHORIZED REDIRECT URI`` in Google's developer site
 5. Grab **Client ID** and **Client Secret**
 6. Fill ``GOOGLE_OAUTH2_CLIENT_ID`` in ``settings.py``
 7. Fill ``GOOGLE_OAUTH2_CLIENT_SECRET`` in ``settings.py``

======
Github
======

 1. Go to https://github.com/settings/applications
 2. Create an app, specify your website domain
 3. Grab **Client ID** and **Client Secret**
 4. Fill ``GITHUB_APP_ID`` in ``settings.py``
 5. Fill ``GITHUB_API_SECRET`` in ``settings.py``

====================
Reload configuration
====================

After any change to ``settings.py`` you will have to restart your application server::

    supervisorctl restart uwsgi
