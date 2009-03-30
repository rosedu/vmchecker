#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Evaluates one homework.

Usage:
    ./commander.py directory - where directory contains (see submit.py)
        `archive.zip' `tests.zip' `config' `storer' `callback'


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

_logger = logging.getLogger('vmchecker.commander')


def _env_with_python_module_search_path():
    """ Setup python module search path to include '$VMCHECKER_ROOT/bin'
    so that the callback python script can access misc, vmcheckerpaths, etc.
    """
    e = os.environ
    module_search_path = os.path.join(vmcheckerpaths.root(), 'bin')
    if 'PYTHONPATH' in e.keys():
        newval = os.pathsep.join(e['PYTHONPATH'], module_search_path)
    e['PYTHONPATH'] = module_search_path
    return e


def _run_callback(dir, ejobs):
    """Runs callback script to upload results"""

    args = (join(dir, 'callback'), join(dir, 'config'))
    args += tuple(join(ejobs, f) for f in _FILES_TO_SEND)

    _logger.info('Homework evaluated; sending results')
    _logger.debug('calling %s', args)

    try:
        env = _env_with_python_module_search_path()
        check_call(args=args, env=env)
    except:
        _logger.error('Sending results failed')
        raise


def _run_executor(machine, assignment):
    # starts job
    # XXX lots of wtf per minute
    # parsing config should be executors' job
    tester = misc.tester_config()
    args = [
            # '/bin/echo',
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
    _logger.info('Begin homework evaluation')
    _logger.debug('calling %s', args)

    try:
        check_call(args)
    except:
        _logger.error('failed to run VMExecutor')
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
    except:
        _logger.exception('failed miserable')
        with open(join(ejobs, 'job_errors'), 'wb') as handler:
            print >>handler, 'VMExecutor died. Please contact administrators.'
        raise
    finally:
        try:
            _run_callback(dir, ejobs)
        except:
            _logger.exception('cannot run callback')

        # clears files
        shutil.rmtree(ejobs)

    _logger.info('all done')


def _print_help():
    print >>sys.stderr, """Usage:
    ./commander.py directory - where directory contains (see submit.py)
        `archive.zip' `tests.zip' `config' `storer' `callback'"""


def _check_required_files(path):
    found_all = True
    needed_files = ['archive.zip', 'tests.zip', 'config', 'storer', 'callback']
    found_files = os.listdir(path)
    for need in needed_files:
        if not need in found_files:
            _logger.error('Could not find necessary file [%s] in [%s]' % (
                    need, path))
            found_all = False
    if not found_all:
        exit(-1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 2:
        print >>sys.stderr, 'Invalid number of arguments.'
        _print_help()
        exit(1)

    start_dir = sys.argv[1]
    if not os.path.isdir(start_dir):
        print >>sys.stderr, 'Not a directory', start_dir
        _print_help()
        exit(1)
    _check_required_files(start_dir)
    main(start_dir)
