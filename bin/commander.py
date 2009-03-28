#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Commander

./commander.py directory

directory contains: homework.zip tests.zip config vmchecker_storer.ini

This commander is a major HACK (ie lots of wtf)

"""

from __future__ import with_statement

__author__ = 'Alexandru Moșoi <brtzsnr@gmail.com>'


import ConfigParser
import logging
import shutil
import sys
from subprocess import check_call
from os.path import join

import misc
import vmcheckerpaths


def main(dir):
    # reads assignment config
    with open(join(dir, 'config')) as handle:
        config = ConfigParser.RawConfigParser()
        config.readfp(handle)

    # reads vmchecker_storer.ini
    with open(join(dir, 'storer')) as handle:
        storer = ConfigParser.RawConfigParser()
        storer.readfp(handle)

    assignment = config.get('Assignment', 'Assignment')
    machine = storer.get(assignment, 'Machine')

    # copies files to where vmchecker expects them (wtf
    shutil.copy(        # copies assignment
        join(dir, 'archive.zip'),
        vmcheckerpaths.abspath('executor_jobs', 'file.zip'))
    shutil.copy(        # copies tests
        join(dir, 'tests.zip'),
        vmcheckerpaths.abspath('executor_jobs', 'tests.zip'))

    # starts job
    # XXX lots of wtf per minute
    # parsing config should be executors' job
    tester = misc.tester_config()
    args = [
            vmcheckerpaths.abspath('VMExecutor/vm_executor'),
            machine,
            '1',                                      # enables kernel_messages
            tester.get(machine, 'VMPath'),
            tester.get('Global', 'LocalAddress'),     # did I review commander.cpp?
            tester.get(machine, 'GuestUser'),
            tester.get(machine, 'GuestPassword'),     # XXX keys?
            tester.get(machine, 'GuestBasePath'),
            tester.get(machine, 'GuestShellPath'),
            tester.get(machine, 'GuestHomeInBash'),   # why is this needed?
            vmcheckerpaths.root(),
            assignment,
            ]

    logging.debug('calling VMExecutor: %s' % args)
    check_call(args)




    # upload_results (callback)

    # clear stuff


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    assert len(sys.argv) == 2
    main(sys.argv[1])
