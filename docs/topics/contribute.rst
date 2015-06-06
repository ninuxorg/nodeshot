**********
Contribute
**********

.. warning::
    Don't wanna be a sucker right? Follow all the steps in this guide and everybody will be happy :-)

This document describes **how to contribute to nodeshot**.

=================================
1. Checkout open issues on github
=================================

The `list of issues on Github`_ is a great place to start looking for things to do.

.. _list of issues on Github: https://github.com/ninuxorg/nodeshot/issues

========================
2. Join the Mailing List
========================

It would be great if you announced your intentions in the `Mailing List`_.

.. _Mailing List: http://ml.ninux.org/mailman/listinfo/nodeshot

That way we can **coordinate** and hopefully **support** you if you have questions.

=======================
3. Fork the github repo
=======================

`Fork the nodeshot repository`_!

That's where you can work on your changes before pushing them upstream.

.. _Fork the nodeshot repository: https://github.com/ninuxorg/nodeshot/fork

===================================
4. Install nodeshot for development
===================================

Follow the procedure described in :doc:`install_development`.

==============================
5. Learn how to run unit tests
==============================

Learn how to run unit tests in :ref:`test-env`.

===========================================
6. Follow PEP8, Style Guide for Python Code
===========================================

Before writing any line of code, please ensure you have read and understood `PEP 8 Style Guide for Python Code`_.

When more people are writing code **it is very important to stay consistent**.

.. _PEP 8 Style Guide for Python Code: http://legacy.python.org/dev/peps/pep-0008/

=====================
7. Start writing code
=====================

Now you can finally start writing code!

============================
8. Write tests for your code
============================

Whether you are fixing a bug or adding a feature to an existing module, you should
ensure that whenever a behaviour is changed there is an automated test that verifies
that the code you wrote is behaving as expected.

`More information about writing tests for django apps`_.

.. _More information about writing tests for django apps: https://docs.djangoproject.com/en/dev/topics/testing/

==================================================
9. Ensure tests pass and coverage is not under 90%
==================================================

Ensure that all the tests pass and that test coverage is not under 90%.

More info on :ref:`test-coverage`.

=========================
10. Document your changes
=========================

If you are adding features to modules or changing the default behaviour
ensure to document your changes by editing the files in the ``/docs`` folder.

Read more about this topic in :ref:`build-the-docs`.

=====================
11. Open pull request
=====================

Now you can finally open a **pull request** on **github** for review.

Optionally, you could open a pull request right after the first commit, so that
the participants can review your commits as you push them.

==============================================
12. Acknowledge Continuous Integration Testing
==============================================

Each time commits are sent to the master branch or are added to a pull request,
the test suite is automatically run on **travis-ci.org**, the result is shown in
the **"build status"** which can either be *failed* or *passed*.

You can `check the build status at travis-ci.org`_.

.. _check the build status at travis-ci.org: https://travis-ci.org/ninuxorg/nodeshot

=======================================
13. Adding features in separate modules
=======================================

If you plan to add dramatic new features to nodeshot, it might better to explore
the possibility of writing a new python package in a separate repository.

Find more information on `How to write reusable apps`_.

.. _How to write reusable apps: https://docs.djangoproject.com/en/dev/intro/reusable-apps/
