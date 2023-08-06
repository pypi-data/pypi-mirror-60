3GPP specification downloader
=============================

|pipeline| |coverage|

.. |pipeline| image:: https://gitlab.com/blueskyjunkie/download_3gpp/badges/master/pipeline.svg
   :target: https://gitlab.com/blueskyjunkie/download_3gpp/commits/master
   :alt: pipeline status

.. |coverage| image:: https://gitlab.com/blueskyjunkie/download_3gpp/badges/master/coverage.svg
   :target: https://gitlab.com/blueskyjunkie/download_3gpp/commits/master
   :alt: coverage report

|pypiVersion|

.. |pypiVersion| image:: https://badge.fury.io/py/download_3gpp.svg
   :target: https://badge.fury.io/py/download_3gpp
   :alt: latest PyPI version

A command line utility for downloading standards documents from the 3GPP download site.

.. contents::

.. section-numbering::


Installation
------------

Use pip to install the package into your virtual environment:

.. code-block:: bash

   pip install download_3gpp


Getting started
---------------

.. code-block:: bash

   > download_3gpp --help

   usage: download_3gpp [-h] [--base-url BASE_URL] [--destination DESTINATION]
                        [--rel REL] [--series SERIES] [--std STD]

   Acquire 3GPP standards packages from archive

   optional arguments:
     -h, --help            show this help message and exit
     --base-url BASE_URL   Base 3GPP download URL to target, default
                           "https://www.3gpp.org/ftp/Specs/latest/"
     --destination DESTINATION
                           Destination download directory, default "./"
     --rel REL             3GPP release number to target, default "all"
     --series SERIES       3GPP series number to target, default "all"
     --std STD             3GPP standard number to target, default "all"


By default, the utility will just download all the latest documents from all the releases in the
3GPP "latest" archive and deposit them in the current directory in the same directory tree as the
download site.

For example

.. code-block:: bash

   download_3gpp

downloads all the "latest" documents in all releases and all series to the default location of the
current directory.

You can download all documents from a specific 3GPP release using the ``--rel`` argument.

.. code-block:: bash

   download_3gpp --rel 16

You can download all documents from a 3GPP series across multiple releases using the ``--series``
argument.

.. code-block:: bash

   download_3gpp --series 32

Combining the ``--rel`` and ``--series`` arguments narrows the filter to that series in the
specified release.

.. code-block:: bash

   download_3gpp --rel 16 --series 32

You can also specify the standard number

.. code-block:: bash

   download_3gpp --std 104

This will download any standard in any series in any release that uses the 104 number; probably a
little too open-ended for most purposes. This is more likely what you want.

.. code-block:: bash

   download_3gpp --series 25 --std 104

This will try to acquire that series/std for all releases. If there is any release where that
document didn't exist then a warning is issued to the console and the download will continue for
any remaining releases.

Unfortunately there is not yet a method to specify a subset of releases to download from, or
exclude specified releases from download so you will have to manually download from each release
that you know the document exists in:

.. code-block:: bash

   download_3gpp --rel 13 --series 25 --std 104
   download_3gpp --rel 16 --series 25 --std 104

3GPP specifications are "snap-shotted" over time, although many of the snapshots have been archived
such that they are no longer publicly available. If you want to acquire standards from a
historical snapshot (first checking that it has the files available for download that you expect)
then specify the base URL, thus:

.. code-block:: bash

   download_3gpp --base-url https://www.3gpp.org/ftp/Specs/2019-09/


Contributions
-------------

Contributions are welcome. If you'd like to make a contribution, send me a pull/merge request. The
contribution must assign copyright to me and in return I will acknowledge you as a contributor to
the project in this document (and of course Gitlab history will also reflect your contribution in
commit history).

Feature requests are also welcome, but with limited time I may not be able to implement a feature
very promptly. It might be quicker for you to implement it yourself and submit a merge request...
