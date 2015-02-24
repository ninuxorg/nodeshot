*******
Mailing
*******

``nodeshot.community.mailing`` is a django app that provides mainly 2 features:

 * enable users to contact other users and layer managers
 * enable admins to send news or emergency communications to all users or a subset of users

 ``nodeshot.community.mailing`` is enabled by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

==================
Available settings
==================

These are the available customizable settings:

 * ``NODESHOT_MAILING_INWARD_REQUIRE_AUTH``
 * ``NODESHOT_MAILING_INWARD_MAXLENGTH``
 * ``NODESHOT_MAILING_INWARD_MINLENGTH``
 * ``NODESHOT_MAILING_INWARD_LOG``
 * ``NODESHOT_MAILING_OUTWARD_MAXLENGTH``
 * ``NODESHOT_MAILING_OUTWARD_MINLENGTH``
 * ``NODESHOT_MAILING_OUTWARD_HTML``
 * ``NODESHOT_MAILING_OUTWARD_STEP``
 * ``NODESHOT_MAILING_OUTWARD_DELAY``

NODESHOT_MAILING_INWARD_REQUIRE_AUTH
------------------------------------

**default**: ``True``

Whether only authenticated users are allowed to contact other nodes or not.

NODESHOT_MAILING_INWARD_MAXLENGTH
---------------------------------

**default**: ``2000``

Maximum length of messages sent by users.

NODESHOT_MAILING_INWARD_MINLENGTH
---------------------------------

**default**: ``15``

Minimum length of messages sent by users.

NODESHOT_MAILING_INWARD_LOG
---------------------------

**default**: ``True``

Wether to log messages sent by users in the database or not.

NODESHOT_MAILING_OUTWARD_MAXLENGTH
----------------------------------

**default**: ``9999``

Maximum length of messages sent by admins.

NODESHOT_MAILING_OUTWARD_MINLENGTH
----------------------------------

**default**: ``50``

Minimum length of messages sent by admins.

NODESHOT_MAILING_OUTWARD_HTML
-----------------------------

**default**: ``True``

Allow HTML emails for messages sent by admins; useful for newsletters or similar periodic communications.

Will display a WYSIWYG editor in the amdin.

NODESHOT_MAILING_OUTWARD_STEP
-----------------------------

**default**: ``20``

Emails won't be sent all in one go, the sending will be divided in several steps.

This setting configures how many emails to send before pausing for the number of seconds set in ``NODESHOT_MAILING_OUTWARD_DELAY``.

NODESHOT_MAILING_OUTWARD_DELAY
------------------------------

**default**: ``10``

Number of seconds to wait after one *step* (as explained in ``NODESHOT_MAILING_OUTWARD_STEP``) is completed.
