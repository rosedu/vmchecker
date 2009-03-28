#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Evaluates one homework.

Usage:
    ./commander.py directory - where directory contains (see submit.py)
        `homework.zip' `tests.zip' `config' `storer' `callback'


The script parses config and storer and invokes vm_executor with
the requiered arguments.

VMExecutor excepts files in `executor_jobs' so it's not safe
to run two instances of commander simultaneously.

When done `callback' is invoked with arguments
    ./callback config file1 file2 file3 ...
Missing files should be ignored (except config).


NOTE: This commander is a major HACK (ie lots of wtf)
TODO: Split VMExecutor, one for each machine.
"""

from __future__ import with_statement

__author__ = 'Alexandru Moșoi <brtzsnr@gmail.com>'


import ConfigParser
import logging
import shutil
import sys
import os
from subprocess import check_call
from os.path import join, isdir

import misc
import vmcheckerpaths


_FILES_TO_SEND = (
    'job_build',
    'job_run',
    'job_errors',
    'job_results',
    'job_km', )


def _run_callback(dir, ejobs):
    """Runs callback script to upload results"""

    args = (join(dir, 'callback'), join(dir, 'config'))
    args += tuple(join(ejobs, f) for f in _FILES_TO_SEND)

    logging.info('Homework evaluated; sending results')
    logging.debug('calling %s', args)

    try:
        check_call(args)
    except:
        logging.error('Sending results failed')
        raise

def _run_executor(machine, assignment):
    # starts job
    # XXX lots of wtf per minute
    # parsing config should be executors' job
    tester = misc.tester_config()
    args = [
            '/bin/echo',
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
    logging.info('Begin homework evaluation')
    logging.debug('calling %s', args)

    try:
        check_call(args)
    except:
        logging.error('failed to run VMExecutor')
        raise


def main(dir):
    # reads assignment config
    with open(join(dir, 'config')) as handle:
        config = ConfigParser.RawConfigParser()
        config.readfp(handle)

    # reads vmchecker_storer.ini
    with open(join(dir, 'storer')) as handle:
        storer = ConfigParser.RawConfigParser()
        storer.readfp(handle)

    # copies files to where vmchecker expects them (wtf
    # XXX 'executor_jobs' path is hardcoded in executor

    ejobs = vmcheckerpaths.abspath('executor_jobs')
    # cleans up executor_jobs, if not already clean
    if isdir(ejobs):
        shutil.rmtree(ejobs)
    os.mkdir(ejobs)

    shutil.copy(        # copies assignment
        join(dir, 'archive.zip'),
        vmcheckerpaths.abspath('executor_jobs', 'file.zip'))
    shutil.copy(        # copies tests
        join(dir, 'tests.zip'),
        vmcheckerpaths.abspath('executor_jobs', 'tests.zip'))

    try:
        assignment = config.get('Assignment', 'Assignment')
        machine = storer.get(assignment, 'Machine')

        _run_executor(machine, assignment)
        _run_callback(dir, ejobs)

        logging.info('all done')
    except:
        logging.exception('failed miserable')
        raise
    finally:
        # clears files
        shutil.rmtree(ejobs)


def _print_help():
    print >>sys.stderr, """Usage:
    ./commander.py directory - where directory contains (see submit.py)
        `homework.zip' `tests.zip' `config' `storer' `callback'"""


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 2:
        print >>sys.stderr, 'Invalid number of arguments.'
        _print_help()
        exit(1)

    if not os.path.isdir(sys.argv[1]):
        print >>sys.stderr, 'Not a directory', sys.argv[1]
        _print_help()
        exit(1)

    main(sys.argv[1])
