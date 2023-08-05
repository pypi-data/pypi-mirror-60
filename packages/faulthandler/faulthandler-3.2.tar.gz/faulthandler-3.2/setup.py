#!/usr/bin/env python

# Prepare a release:
#
#  - update VERSION: faulthandler.c, setup.py, doc/conf.py
#  - update the changelog: doc/index.rst
#  - run tests on Linux: tox
#  - run tests on Windows: py -2.7-64 -m tox -r
#  - run tests on Windows: py -2.7-32 -m tox -r
#  - set release date in the changelog: doc/index.rst
#  - git commit -a
#  - git push
#  - check Travis CI status:
#    https://travis-ci.org/vstinner/faulthandler
#
# Release a new version:
#
#  - git tag X.Y
#  - git push
#  - git push --tags
#  - On Linux:
#
#    * git clean -fdx
#    * python2 setup.py sdist
#    * twine upload dist/*
#
#  - Build 32-bit and 64-bit wheel packages on Windows:
#
#    * py -2.7-64 setup.py bdist_wheel upload
#    * py -2.7-32 setup.py bdist_wheel upload
#    * (pip install wheel if bdist_wheel is missing)
#
# After the release:
#
#  - increment VERSION: faulthandler.c, setup.py, doc/conf.py
#  - git commit -a
#  - git push

from __future__ import with_statement

import platform
import sys
from os.path import join as path_join
from os.path import basename
from os.path import dirname
from distutils.command.build import build
from setuptools import Command
from setuptools import Extension
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.easy_install import easy_install


VERSION = "3.2"

FILES = ['faulthandler.c', 'traceback.c']

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Programming Language :: C',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


def python_implementation():
    if hasattr(sys, 'implementation'):
        # PEP 421, Python 3.3
        return sys.implementation.name
    else:
        return platform.python_implementation()


if sys.version_info >= (3, 3):
    print("ERROR: faulthandler is a builtin module since Python 3.3")
    sys.exit(1)


if python_implementation().lower() != 'cpython':
    print("ERROR: faulthandler is written for CPython, it doesn't work on %s"
          % python_implementation())
    print("faulthandler builtin PyPy since PyPy 5.5: use pypy -X faulthandler")
    sys.exit(1)


class BuildWithPTH(build):
    def run(self):
        build.run(self)
        path = path_join(dirname(__file__), 'faulthandler.pth')
        dest = path_join(self.build_lib, basename(path))
        self.copy_file(path, dest)


class EasyInstallWithPTH(easy_install):
    def run(self):
        easy_install.run(self)
        path = path_join(dirname(__file__), 'faulthandler.pth')
        dest = path_join(self.install_dir, basename(path))
        self.copy_file(path, dest)


class DevelopWithPTH(develop):
    def run(self):
        develop.run(self)
        path = path_join(dirname(__file__), 'faulthandler.pth')
        dest = path_join(self.install_dir, basename(path))
        self.copy_file(path, dest)


class GeneratePTH(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        with open(path_join(dirname(__file__), 'faulthandler.pth'), 'w') as fh:
            with open(path_join(dirname(__file__), 'faulthandler.embed')) as sh:
                fh.write(
                    'import os, sys;'
                    'exec(%r)' % sh.read().replace('    ', ' ')
                )


with open('README.rst') as f:
    long_description = f.read().strip()

options = {
    'name': "faulthandler",
    'version': VERSION,
    'license': "BSD (2-clause)",
    'description': 'Display the Python traceback on a crash',
    'long_description': long_description,
    'url': "https://faulthandler.readthedocs.io/",
    'author': 'Victor Stinner',
    'author_email': 'victor.stinner@gmail.com',
    'ext_modules': [Extension('faulthandler', FILES)],
    'classifiers': CLASSIFIERS,
    'cmdclass': {
        'build': BuildWithPTH,
        'easy_install': EasyInstallWithPTH,
        'develop': DevelopWithPTH,
        'genpth': GeneratePTH,
    },
}

setup(**options)

