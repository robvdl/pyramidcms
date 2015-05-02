PyramidCMS
==========

.. image:: https://img.shields.io/travis/robvdl/pyramidcms.svg
    :target: https://travis-ci.org/robvdl/pyramidcms
    :alt: Travis CI

.. image:: https://img.shields.io/coveralls/robvdl/pyramidcms.svg
    :target: https://coveralls.io/r/robvdl/pyramidcms
    :alt: Coveralls

.. image::  https://img.shields.io/codeclimate/github/robvdl/pyramidcms.svg
    :target: https://codeclimate.com/github/robvdl/pyramidcms
    :alt: Code Climate

A content management system for Pyramid and Python 3.3+

Note that PyramidCMS development has only just started and we are mostly
still working on the foundation, so there isn't really much to see here yet.

We do welcome new contributors, but we are still in the early stages of the
project, so it will take a while before it will even be remotely usable.

We want to use only the latest version of Python (3.3 or higher), as this
it is still a young project so we can aim high now and use the latest language
features and builtin libraries, also by only targeting Python 3, the codebase
is kept clean and tidy.

First create a development environment, it must use Python 3::

    mkvirtualenv pyramidcms -p /usr/bin/python3
    git clone git@github.com:robvdl/pyramidcms.git
    cd pyramidcms
    python setup.py develop

Once pyramidcms is installed, you need to create a project to work with,
first change to another directory as you don't want to create the project
inside the pyramidcms folder itself. Lets just go one directory up, then
create a new project::

    cd ..
    pcreate -s pyramidcms foo

Once a project has been created, change to that directory and install it too::

    cd foo
    python setup.py develop

When that is done, run Alembic to create the database tables::

    pcms migrate development.ini

Note that this is exactly the same as running the following command,
the "pcms migrate" command is just a handy wrapper command::

    alembic -c development.ini upgrade head

Now load the following "temporary" testing data::

    pcms loaddata development.ini

Note that in the future the loadata command will load any JSON fixture file,
given through a command line argument to the loaddata command. For now it just
inserts some test data, some users, groups and permissions for development.

When everything is installed, this will start the web application::

    gunicorn --paste development.ini

Running the tests
-----------------

Switch back to the pyramidcms folder, make sure you have installed the dev
requirements as well::

    pip install -r requirements/dev.txt

Now just run nosetests to run the tests::

    nosetests

You can also use Tox to run the tests against multiple Python versions::

    tox

To do so, you must have both Python 3.3 and 3.4 installed, on Ubuntu this
can be done using the "Deadsnakes PPA".
