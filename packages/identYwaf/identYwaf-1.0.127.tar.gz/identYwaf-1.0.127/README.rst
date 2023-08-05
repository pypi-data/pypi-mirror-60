identYwaf
=========

|Build Status| |Python 2.x|3.x| |License|

**identYwaf** is an identification tool that can recognize web
protection type (i.e. WAF) based on blind inference. Blind inference is
being done by inspecting responses provoked by a set of predefined
offensive (non-destructive) payloads, where those are used only to
trigger the web protection system in between (e.g.
``http://<host>?aeD0oowi=1 AND 2>1``). Currently it supports more than
80 different protection products (e.g. ``aeSecure``, ``Airlock``,
``CleanTalk``, ``CrawlProtect``, ``Imunify360``, ``MalCare``,
``ModSecurity``, ``Palo Alto``, ``SiteGuard``, ``UrlScan``, ``Wallarm``,
``WatchGuard``, ``Wordfence``, etc.), while the knowledge-base is
constantly growing.

.. figure:: https://i.imgur.com/tSOAgnn.png
   :alt: Screenshot

For more information you can check `slides`_ for a talk "**Blind WAF
identification**" held at *Sh3llCON 2019* (Santander / Spain).

Installation
------------

You can use pip to install and/or upgrade the identYwaf to latest (PyPI) version with: ::

    pip install --upgrade identYwaf

Alternatively, you can download the latest tarball by clicking
`here <https://github.com/stamparm/identYwaf/tarball/master>`__ or
latest zipball by clicking
`here <https://github.com/stamparm/identYwaf/zipball/master>`__.

identYwaf works out of the box with
`Python <http://www.python.org/download/>`__ version **2.6**, **2.7** and
**3.x** on any platform.

Usage
-----

To get a list of basic options and switches use:

::

    identYwaf -h

.. _slides: https://www.slideshare.net/stamparm/blind-waf-identification

.. |Build Status| image:: https://api.travis-ci.org/stamparm/identYwaf.svg?branch=master
   :target: https://travis-ci.org/stamparm/identYwaf
.. |Python 2.x|3.x| image:: https://img.shields.io/badge/python-2.x|3.x-yellow.svg
   :target: https://www.python.org/
.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/stamparm/identYwaf/blob/master/LICENSE

