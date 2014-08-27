PyramidCMS
==========

A content management system for Pyramid and Python 3.

Note that PyramidCMS development has only just started, so there isn't
really much to see here at this point.

We do welcome new contributors, but at this point we are still in the
planning stages of the project.

Setting up a development environment::

    mkvirtualenv pyramidcms -p /usr/bin/python3
    git clone git@github.com:robvdl/pyramidcms.git
    cd pyramidcms
    ./setup.py develop
    pcms_initdb
    pserve development.ini

