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
      version = '0.5',
      author = 'vmchecker',
      author_email = 'vmchecker-dev@lists.rosedu.org',
      url = 'http://github.com/vmchecker/vmchecker/tree/master',
      description = 'An online homework evaluator',
      license = 'MIT',
      platforms = 'Linux',
      packages = ['vmchecker'],
      package_dir =  {'vmchecker': 'vmchecker'},
      package_data = {'vmchecker': ['examples/config-template',
                                    'examples/so-linux_vmchecker_build.sh',
                                    'examples/so-linux_vmchecker_run.sh',
                                    'examples/so-win_vmchecker_build.sh',
                                    'examples/so-win_vmchecker_run.sh',
                                    ]},
      scripts = ['bin/vmchecker-init-course',
                 'bin/vmchecker-queue-manager',
                 'bin/vmchecker-submit',
                 'bin/vmchecker-resubmit',
                 'bin/vmchecker-update-db',
                 'bin/vmchecker-vm-executor',
                 'bin/vmchecker-view-grades',
                 ],
      data_files = [#('/etc/init.d/', ['etc/init.d/vmchecker']),
	            ('/etc/vmchecker/', ['etc/vmchecker/config.list',
                                         'etc/vmchecker/ldap.config',
                                         'etc/vmchecker/acl.config',
                                         ])])

