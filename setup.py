#!/usr/bin/env python

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
