=============================
django-dj-plugin
=============================

.. image:: https://badge.fury.io/py/django-dj-plugin.svg
    :target: https://badge.fury.io/py/django-dj-plugin

.. image:: https://travis-ci.org/daimon99/django-dj-plugin.svg?branch=master
    :target: https://travis-ci.org/daimon99/django-dj-plugin

.. image:: https://codecov.io/gh/daimon99/django-dj-plugin/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/daimon99/django-dj-plugin

Django plgooge practice modules.

Documentation
-------------

The full documentation is at https://django-dj-plugin.readthedocs.io.

Quickstart
----------

Install django-dj-plugin::

    pip install django-dj-plugin

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_dj_plugin.apps.DjangoDjPluginConfig',
        ...
    )

Add django-dj-plugin's URL patterns:

.. code-block:: python

    from django_dj_plugin import urls as django_dj_plugin_urls


    urlpatterns = [
        ...
        url(r'^', include(django_dj_plugin_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
