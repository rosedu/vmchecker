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
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build

import os

class build_trans(cmd.Command):
    description = 'Compile .po files into .mo files'
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        name = self.distribution.get_name()
        po_dir = os.path.join(os.path.dirname(os.curdir), os.path.join(self.distribution.package_dir[name], 'po'))
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:-3]
                    src = os.path.join(path, f)
                    dest_path = os.path.join('build', 'locale', lang, 'LC_MESSAGES')
                    dest = os.path.join(dest_path, name + '.mo')
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    if not os.path.exists(dest):
                        print 'Compiling %s' % src
                        os.system("msgfmt -c " + src + " -o " + dest)
#                        msgfmt.make(src, dest)
                    else:
                        src_mtime = os.stat(src)[8]
                        dest_mtime = os.stat(dest)[8]
                        if src_mtime > dest_mtime:
                            print 'Compiling %s' % src
#                            msgfmt.make(src, dest)
                            os.system("msgfmt -c " + src + " -o " + dest)

class build(_build):
    sub_commands = _build.sub_commands + [('build_trans', None)]
    def run(self):
        _build.run(self)

class install_data(_install_data):

    def run(self):
        name = self.distribution.get_name()
        for lang in os.listdir('build/locale/'):
            lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', name + '.mo')
            self.data_files.append( (lang_dir, [lang_file]) )
        _install_data.run(self)

cmdclass = {
    'build': build,
    'build_trans': build_trans,
    'install_data': install_data,
}

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
                                    'examples/auth_file.json',
                                    ]},
      scripts = ['bin/vmchecker-init-course',
                 'bin/vmchecker-queue-manager',
                 'bin/vmchecker-submit',
                 'bin/vmchecker-resubmit',
                 'bin/vmchecker-reset-db',
                 'bin/vmchecker-update-db',
                 'bin/vmchecker-vm-executor',
                 'bin/vmchecker-view-grades',
                 'bin/vmchecker-team-manager',
                 'bin/vmchecker-download-external-files',
                 ],
      data_files = [('/etc/init.d/', ['etc/init.d/vmchecker']),
	            ('/etc/vmchecker/', ['etc/vmchecker/config.list',
                                         'etc/vmchecker/ldap.config',
                                         'etc/vmchecker/acl.config',
                                         ])],
      cmdclass = cmdclass)

