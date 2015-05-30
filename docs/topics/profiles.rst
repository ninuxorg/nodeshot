********
Profiles
********

``nodeshot.community.profiles`` is a django app that adds the following features
to the RESTful API:

 * user profiles
 * user registration
 * email confirmation
 * email address management (add multiple email addresses)
 * login
 * logout

==================
Available settings
==================

``nodeshot.community.profiles`` is enabled by default in ``nodeshot.conf.settings.INSTALLED_APPS``.

These are the available customizable settings:

 * ``NODESHOT_PROFILES_REGISTRATION_OPEN``
 * ``NODESHOT_PROFILES_EMAIL_CONFIRMATION``
 * ``NODESHOT_PROFILES_REQUIRED_FIELDS``

NODESHOT_PROFILES_REGISTRATION_OPEN
-----------------------------------

**default**: ``True``

Indicates wheter registration is open to the public.

NODESHOT_PROFILES_EMAIL_CONFIRMATION
------------------------------------

**default**: ``True``

Indicates wheter new users have to confirm their email.

NODESHOT_PROFILES_REQUIRED_FIELDS
---------------------------------

**default**: ``['email']``

Required fields during registration.

Fields added at the moment won't be yet reflected in ``nodeshot.ui.default``.
