#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

with open(os.path.join(here, 'requirements/base.txt')) as f:
    requires = [l.strip() for l in f.readlines()]

with open(os.path.join(here, 'requirements/dev.txt')) as f:
    dev_requires = [l.strip() for l in f.readlines()]

setup(
    name='pyramidcms',
    version='0.0',
    description='Content management system in Pyramid',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Rob van der Linde',
    author_email='robvdl@gmail.com',
    url='https://github.com/robvdl/pyramidcms',
    keywords='web wsgi bfg pylons pyramid cms',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=dev_requires,
    extras_require={'dev': dev_requires},
    test_suite='nose.collector',
    entry_points="""\
    [paste.app_factory]
    main = pyramidcms:main
    [console_scripts]
    pcms_initdb = pyramidcms.scripts.initdb:main
    """,
)
