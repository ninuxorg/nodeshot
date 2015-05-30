*****************
Automated install
*****************

This section describes how to perform a quick install of Nodeshot on **Ubuntu / Debian systems**.

.. warning::
    This procedure has been tested on clean installs of **Debian 7**, **Ubuntu 13.10** and **Ubuntu 14.04 LTS**.

    If you try it on a server where other applications are running you might incur in some errors.

    The most typical would be having the port 80 already in use by Apache.

    In that case, you should consider using the :doc:`manual_install` procedure in order to install according to your needs.

=============
Prerequisites
=============

First of all, we need to install the `Fabric`_ Python library.

.. _Fabric: http://www.fabfile.org/index.html

To install fabric, you need to have pip installed on your system. See `how to install pip`_ first.

.. _how to install pip: http://pip.readthedocs.org/en/latest/installing.html

Proceed to install Fabric::

    pip install fabric

More detailed instructions about Fabric installation can be found `here`_.

.. _here: http://www.fabfile.org/installing.html

=========================
Download nodeshot-fabfile
=========================

Download the archive:

 * *tarball*: https://github.com/ninuxorg/nodeshot-fabfile/tarball/master
 * *zip*: https://github.com/ninuxorg/nodeshot-fabfile/archive/master.zip

eg::

    wget https://github.com/ninuxorg/nodeshot-fabfile/archive/master.zip -O nodeshot-fabfile.zip
    unzip nodeshot-fabfile.zip
    rm nodeshot-fabfile.zip
    cd nodeshot-fabfile-master

================
Start installing
================
.. warning::
    We suggest to install on a clean virtual machine

Start the fabfile script with::

    fab install -H <remote_host> -u <user> -p <password>

``<user>`` should be either a sudoer or root.

The install procedure will start, asking you to insert the parameters that will customize your nodeshot instance:

.. image:: images/deploy1.png

These are the informations you will have to supply to the install procedure:

**Install directory**: the directory where Nodeshot will be installed ( default: /var/www/)

**Project name**: the name for your project (default: myproject), **avoid using nodeshot, test, or other existing python packages or the installer will break**

**Server name**: the FQDN of your server (no default)

**Database user**: postgres owner of Nodeshot DB (default: nodeshot)

**Database user password**: password for postgres owner of Nodeshot DB (default generated randomly)

Next, you will have to supply the details for the SSL certificate that will be used for serving Nodeshot over HTTPS:

.. image:: images/deploy2.png

That's all you have to do: the installation process will start.

It will take care of installing package dependencies,
creating a python virtualenv, configuring the webserver and the all the other bits needed to run Nodeshot.

The installation will take about 5-10 minutes to complete.
As final step, it will start all services and leave you with a full running version of Nodeshot.

A message will remind you to change the default admin account password:

.. image:: images/deploy4.png

=============================
Updating an existing instance
=============================

To run an update do::

    fab update -H <remote_host> -u <user> -p <password>

If you need to specify parameters without the need to be prompted do::

    fab update:use_defaults=True,project_name=<project_name> -H <remote_host> -u <user> -p <password>

You could also set a different ``root_dir`` with::

    fab update:use_defaults=True,root_dir=/custom/path/,project_name=<project_name> -H <remote_host> -u root -p <password>

======================================
Install on a VM hosted on your machine
======================================

The above procedure can be also executed on a Virtual Machine following the instructions below.

For this purpose we'll be using `VirtualBox`_  and `Vagrant`_ , a platform for configuring lightweight, reproducible, and portable development environments.

.. _VirtualBox: https://www.virtualbox.org/
.. _Vagrant: http://www.vagrantup.com/

------------
Installation
------------
Informations on how to install **VirtualBox** and **Vagrant** on different platforms can be found on their respective websites.

On a Ubuntu Linux distribution it's as easy as::

    apt-get install virtualbox
    apt-get install vagrant

-------------
Configuration
-------------

**VirtualBox**

You will need to add a private virtual network interface, in order to enable communication between your host and the Vagrant VM::

    VBoxManage hostonlyif create
    VBoxManage hostonlyif ipconfig vboxnet0 --ip <host private ip address. e.g: 192.168.56.1>

**Vagrant**

Configure Vagrant VM network and enable root access on it::

    # Create a directory for your Vagrant VMs
    mkdir vagrantVM_Dir
    cd vagrantVM_Dir
    # Initialize a Ubuntu 12.04 VM ( use hashicorp/precise32 or hashicorp/precise64 depending on your system)
    vagrant init hashicorp/precise64
    # Edit Vagrantfile and create a host-only private network which allows host-only access to the machine
    vim Vagrantfile
    # Uncomment line 27 and change the IP address according to the one you defined for your host
    # e.g. config.vm.network "private_network", ip: "192.168.56.2"

    # Start Vagrant
    vagrant up
    # ssh into VM and abilitate root login
    vagrant ssh
    vagrant@precise64:~$ sudo -i
    root@precise64:~# passwd root
    Enter new UNIX password:
    Retype new UNIX password:
    passwd: password updated successfully

Once completed the above steps, you can run the Nodeshot install procedure as you would do on a remote host::

    fab install -H <VM ip address> -u root -p password
