..
    Copyright (C) 2019 CIS UCT Prague.

    OARepo profiler is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

======================
OARepo profiler
======================

.. image:: https://img.shields.io/github/license/oarepo/oarepo-profiler.svg
        :target: https://github.com/oarepo/oarepo-profiler/blob/master/LICENSE

.. image:: https://img.shields.io/travis/oarepo/oarepo-profiler.svg
        :target: https://travis-ci.org/oarepo/oarepo-profiler

.. image:: https://img.shields.io/coveralls/oarepo/oarepo-profiler.svg
        :target: https://coveralls.io/r/oarepo/oarepo-profiler

.. image:: https://img.shields.io/pypi/v/oarepo-profiler.svg
        :target: https://pypi.org/pypi/oarepo-profiler

Installation
============

.. code-block:: bash

   pip install oarepo-profiler

Usage
=====

* change the wsgi endpoint from `invenio_app.wsgi:application` to `oarepo_profiler:application`
* to start profiling, add `OAREPO_PROFILER_ENABLED=True` to `invenio.cfg`. Implicitly the `profs` files
  will be created in `/tmp/oarepo-profiler`. This location can be changed by setting
  `OAREPO_PROFILER_PATH`
* use third party tools (such as snakeviz) to interpret the result of profiling

