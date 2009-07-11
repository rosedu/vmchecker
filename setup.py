#!/usr/bin/env python
"""The distutils setup script.

To install vmchecker run
    $ ./setup.py install --home=~
which install vmchecker to ~/lib/python.

Probably, you'll need to setup PYTHONPATH for python
to see your library
    $ export PYTHONPATH=~/lib/python/

You can run tests using
    $ ./tests/run-all.sh

"""

from distutils.core import setup

setup(name = 'vmchecker',
      version = '0.3a1',
      author = 'vmchecker',
      author_email = 'vmchecker-dev@lists.rosedu.org',
      url = 'http://github.com/vmchecker/vmchecker/tree/master',
      description = 'An online homework evaluator',
      license = 'MIT',
      platforms = 'Linux',
      packages = ['vmchecker'],
      package_dir = {'vmchecker': 'lib'})
