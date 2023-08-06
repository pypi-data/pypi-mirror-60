:Author: Jérôme Kieffer
:Date: 31/01/2019
:Keywords: Installation procedure on Linux
:Target: System administrators

Installation procedure on Linux
===============================

We cover first Debian-like distribution, then a generic recipie for all other
version is given.

Installation procedure on Debian/Ubuntu
---------------------------------------

PyFAI has been designed and originally developed on Ubuntu 10.04 and debian6.
Now, the pyFAI library is included into debian7, 8, 9 and any recent Ubuntu and
Mint distribution.
To install the package provided by the distribution, use:

.. code-block:: shell

   sudo apt-get install pyfai

The issue with distribution based installation is the obsolescence of the version
available.

Debian 7 and Ubuntu 12.04
.........................

To build a more recent version, pyFAI provides you a small scripts which builds a *debian* package and installs it.
It relies on *stdeb* and provides a single package with everything inside.
You will be prompted for your password to gain root access in order to be able to install the freshly built package.

.. code-block:: shell

   sudo apt-get install python-stdeb cython python-fabio
   wget https://github.com/silx-kit/pyFAI/archive/master.zip
   unzip master.zip
   cd pyFAI-master
   ./build-deb7.sh

Debian 8, 9 and newer
.....................

Thanks to the work of Frédéric-Emmanuel Picca, the debian package of pyFAI
provides a pretty good template which allows continuous builds.

From silx repository
++++++++++++++++++++

You can automatically install the latest nightly built of pyFAI with:

.. code-block:: shell

   wget http://www.silx.org/pub/debian/silx.list
   wget http://www.silx.org/pub/debian/silx.pref
   sudo mv silx.list /etc/apt/sources.list.d/
   sudo mv silx.pref /etc/apt/preferences.d/
   sudo apt-get update
   sudo apt-get install pyfai

**Nota:** The nightly built packages are not signed, hence you will be prompted
to install non-signed packages.

Build from sources
++++++++++++++++++

One can also built from sources:

.. code-block:: shell

   sudo apt-get build-dep pyfai
   wget https://github.com/silx-kit/pyFAI/archive/master.zip
   unzip master.zip
   cd pyFAI-master
   ./build-deb.sh


The first line is really long and defines all the dependence tree for building
*debian* package, including debug and documentation.
The build procedure last for a few minutes and you will be prompted for your
password in order to install the freshly built packages.
The *deb-*files, available in the *package* directory are backports for your local
installation.

Installation procedure on other linux distibution
-------------------------------------------------

If your distribution does not provide you pyFAI packages, using the **PIP** way
is advised, via wheels packages. First install *pip* and *wheel*:

.. code-block:: shell

    sudo pip install pyFAI

Or you can install pyFAI from the sources:

.. code-block:: shell

   wget https://github.com/silx-kit/pyFAI/archive/master.zip
   unzip master.zip
   cd pyFAI-master
   python setup.py build test
   sudo pip install . --upgrade

**Nota:** The usage of "python setup.py install" is now deprecated.
It causes much more trouble as there is no installed file tracking,
hence no way to de-install properly the package.
