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
Missing files should be ignored (except config)


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
    # XXX path is hardcoded

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
        logging.exception('failed to run VMExecutor')
        shutil.rmtree(ejobs)
        raise

    # uploads results
    args = (
            join(dir, 'callback'),
            join(dir, 'config'),
            join(ejobs, 'job_build'),
            join(ejobs, 'job_run'),
            join(ejobs, 'job_errors'),
            join(ejobs, 'job_results'),
            join(ejobs, 'job_km'),
        )
    logging.info('Homework evaluated; sending results')
    logging.debug('calling %s', args)
    try:
        check_call(args)
    except:
        logging.exception('Sending results failed')
        shutil.rmtree(ejobs)
        raise

    # clears files
    shutil.rmtree(ejobs)
    logging.info('all done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    assert len(sys.argv) == 2
    main(sys.argv[1])
