=============================
Django Smithy
=============================

.. image:: https://badge.fury.io/py/django-smithy.svg
    :target: https://badge.fury.io/py/django-smithy

.. image:: https://travis-ci.org/jamiecounsell/django-smithy.svg?branch=master
    :target: https://travis-ci.org/jamiecounsell/django-smithy

.. image:: https://codecov.io/gh/jamiecounsell/django-smithy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jamiecounsell/django-smithy

Craft HTTP requests in the Django Admin. Django Smithy is an HTTP Request templating system that allows developers to build systems to send abstract messages without additional development.

Documentation
-------------

The full documentation is at https://django-smithy.readthedocs.io.

Quickstart
----------

Install Django Smithy::

    pip install django-smithy

Then, create a request template to send:

.. image:: https://user-images.githubusercontent.com/2321599/54481318-90a2ba80-4809-11e9-96ae-46be38ad65d3.png


Features
--------

* Design requests in the Django Admin panel
* Send requests with whatever context you'd like
* Use Django's templating system everywhere
* Define variables to be added to the context

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
