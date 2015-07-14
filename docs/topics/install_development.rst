************************
Development Installation
************************

.. warning::
    This installation guide is designed for debian based operating systems.

    Other Linux distributions are good as well but the name of some packages may vary.

This document describes how to install nodeshot for **development**.

We are assuming you are executing commands as a **sudoer** user but **not root**.

Related pages: :doc:`Contribute to nodeshot <contribute>`.

.. _install-dependencies-dev:

====================
Install dependencies
====================

First of all, update your apt cache::

    sudo apt-get update --fix-missing

Install development packages::

    sudo apt-get install python-software-properties software-properties-common build-essential libxml2-dev python-setuptools python-virtualenv python-dev binutils libjson0-dev libjpeg-dev libffi-dev wget git

Install postgresql, postgis and geospatial libraries::

    sudo apt-get install postgis* libproj-dev gdal-bin libpq-dev libgdal1-dev python-gdal

.. _create-database-dev:

===============
Create database
===============

Become ``postgres`` user::

    sudo su postgres

Create database, create required postgresql extensions,
create a superuser::

    createdb nodeshot
    psql nodeshot
    CREATE EXTENSION postgis;
    CREATE EXTENSION hstore;
    CREATE USER nodeshot WITH PASSWORD 'your_password';
    ALTER USER nodeshot SUPERUSER;

exit (press CTRL+D) and go back to being your user::

    exit

.. _install-python-packages-dev:

=======================
Install python packages
=======================

First of all, install virtualenvwrapper (systemwide)::

    sudo pip install virtualenvwrapper

virtualenvwrapper needs some initialization before you can use its shortcuts::

    echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
    source ~/.bashrc

Create a **python virtual environment**, which is a self-contained python installation
which will contain all the python packages required by nodeshot::

    mkvirtualenv nodeshot

Update the basic python utilities::

    pip install -U setuptools pip wheel

Clone your fork in your favourite location (``/home/<user>`` or ``/var/www``), have you `forked nodeshot`_, right?

.. code-block:: bash

    git clone git@github.com:<YOUR-FORK>/nodeshot.git
    cd nodeshot

Replace ``<YOUR-FORK>`` with your github username (be sure to have `forked nodeshot`_ first).

.. _forked nodeshot: https://github.com/ninuxorg/nodeshot/fork

Install the required python packages::

    pip install -r requirements.txt

Finally install nodeshot with::

    python setup.py develop

Create the development project, be sure it's called **dev**:

.. code-block:: bash

    nodeshot startproject dev && cd dev

.. _project-configuration-dev:

=====================
Project configuration
=====================

Open ``settings.py``::

    vim dev/settings.py

And edit the following settings:

* ``DOMAIN``: set localhost
* ``DATABASE['default']['USER']``: set nodeshot
* ``DATABASE['default']['PASSWORD']``: set the password chosen during the :ref:`create-database-dev` step

Create the database tables and initial data:

.. code-block:: bash

    # will prompt you to create a superuser, proceed!
    ./manage.py migrate --no-initial-data && ./manage.py loaddata initial_data

Run the development server::

    ./manage.py runserver

Alternatively, if you need to reach the dev server for other hosts on the same LAN,
you can setup the development server to listen on all the network interfaces::

    ./manage.py runserver 0.0.0.0:8000

Now you can open your browser at http://localhost:8000/ or at http://localhost:8000/admin/.

.. _test-env:

=================================
How to setup the test environment
=================================

The ``/test`` directory contains a nodeshot project called ``ci`` (stands for continuous integration)
that is needed to run automated tests (unit tests, functional tests and regression tests).

Install the hstore extension on template1 according to `how to run tests with django-hstore`_::

    sudo su postgres
    psql template1 -c 'CREATE EXTENSION hstore;'
    exit

.. _how to run tests with django-hstore: http://djangonauts.github.io/django-hstore/#_running_tests

Do a ``cd`` into the ``/test`` dir::

    cd /[PATH-TO-NODESHOT-REPO]/tests

Create a ``local_settings.py`` file::

    cp ci/local_settings.example.py ci/local_settings.py

Ensure your virtualenv is activated::

    workon nodeshot

Run all the tests with::

    ./runtests.py --keepdb

The ``keepdb`` option allows to avoid recreating the test database at each run, **hence saving precious time**.

If you want to speed up tests even more, tweak your local postgresql configuration by setting these values::

    # /etc/postgresql/9.1/main/postgresql.conf
    # only for development!
    fsync = off
    synchronous_commit = off
    full_page_writes = off

Test specific modules
---------------------

Each module has its own tests, so you can test one module at time::

    python manage.py test --keepdb nodeshot.core.nodes

You can also test more modules::

    python manage.py test --keepdb nodeshot.core.nodes nodeshot.core.layers nodeshot.core.cms

.. _test-coverage:

Test coverage
-------------

Install coverage package::

    pip install coverage

Run test coverage and get a textual report::

    coverage run --source=nodeshot runtests.py --keepdb && coverage report

Calculate test coverage for specific modules::

    coverage run --source=nodeshot.core.nodes ./manage.py test --keepdb nodeshot.core.nodes && coverage report

Measure time spent running tests
--------------------------------

Automated tests that involve database calls and/or HTTP requests can quickly become slow.

Slow tests mean low productivity, especially if you are used to **Test Driven Development**.

For this reason, if you notice that some tests are slow, you have two additional options to measure test executition times,
**find out which tests are slow** and refactor them.

Time option
^^^^^^^^^^^

``--time`` will measure how much time is needed to execute each test class.

Detailed option
^^^^^^^^^^^^^^^

``--time --detailed`` will measure how much time is needed to execute each test class **and** each single test.

Examples
^^^^^^^^

Here's a couple of examples::

    # general measurement
    ./runtests.py --keepdb --time

    # detailed measurement
    ./runtests.py --keepdb --time --detailed

    # detailed measurement for a specific test class
    python manage.py test --keepdb --time --detailed nodeshot.core.nodes

.. _build-the-docs:

==============================
How to build the documentation
==============================

Building the documentation locally is useful for several reasons:

* you can read it offline
* you can edit it locally
* you can preview the changes locally before sending any pull request

So let's **build the docs**!

Install sphinx::

    workon nodeshot
    pip install sphinx

Do a ``cd`` into the ``/docs`` dir::

    cd /[PATH-TO-NODESHOT-REPO]/docs

Now build the docs with::

    make html

Quite some html files have been created, you can browse those HTML files in a web browser and it should work.

The format used in the docs is **reStructured Text** while the python package used is **python-sphinx**.

`Read more information about Sphinx and reStructured Text`_.

.. _Read more information about Sphinx and reStructured Text: http://sphinx-doc.org/tutorial.html

.. _contribute-dev:

==========
Contribute
==========

**If you intend to contribute to nodeshot**, be sure to read :doc:`How to contribute to nodeshot <contribute>`.
