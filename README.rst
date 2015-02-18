PyramidCMS
==========

.. image:: https://travis-ci.org/robvdl/pyramidcms.png?branch=master
        :target: https://travis-ci.org/robvdl/pyramidcms

A content management system for Pyramid and Python 3.3+

Note that PyramidCMS development has only just started and we are mostly
still working on the foundation, so there isn't really much to see here yet.

We do welcome new contributors, but we are still in the early stages of the
project, so it will take a while before it will even be remotely usable.

We want to use only the latest version of Python (3.3 or higher), as this
is still a young project so we can aim high and use the latest language
features and core libraries.

Setting up a development environment::

    mkvirtualenv pyramidcms -p /usr/bin/python3
    git clone git@github.com:robvdl/pyramidcms.git
    cd pyramidcms
    ./setup.py develop

Once installed, this will create a local pyramidcms.ini file for development::

    pcms createconfig dev

Once that is done, run Alembic to create the database tables::

    alembic upgrade head

Now load the temporary test data::

    pcms loaddata

Note that in the future the loadata command will load generic JSON fixtures,
but for now it just inserts some test users, groups and permissions.

When everything is installed, this will start the web application::

    gunicorn --paste pyramidcms.ini

Running the tests
-----------------

Make sure you have installed the dev requirements::

    pip install -r requirements/dev.txt

Now just run nose::

    nosetests

Note that if nosetests doesn't work and it appears to be using Python 2
instead of the virtualenv, this is something I ran into on Ubuntu 14.014
as well, just deactivate the virtualenv and type "workon pyramidcms" again.

You can also use Tox to run the tests against multiple Python versions::

    tox

To do so, you must have both Python 3.3 and 3.4 installed, on Ubuntu this
can be done using the "Deadsnakes PPA".
