#!/usr/bin/env python
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
import time
import sys
import os
from subprocess import check_call, Popen
from os.path import join, isdir

import config
import vmcheckerpaths
import assignments


_FILES_TO_SEND = (
    'job_build',
    'job_run',
    'job_errors',
    'job_results',
    'job_km', )
_EXECUTOR_OVERHEAD = 300

_logger = logging.getLogger('vmchecker.commander')


def _env_with_python_module_search_path():
    """ Setup python module search path to include `./bin'
    so that the callback python script can access misc, vmcheckerpaths, etc.

    XXX alexandru says: why is this needed?

    """
    e = os.environ
    module_search_path = os.path.join(vmcheckerpaths.root, 'bin')
    if 'PYTHONPATH' in e.keys():
        module_search_path = os.pathsep.join(
                e['PYTHONPATH'], module_search_path)
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


def _make_test_config(ejobs, machine, timeout, kernel_messages, dst_file):
    km = True if int(kernel_messages) != 0 else False
    test = {
        'km_enable' : km,
        'host' : {
            'vmx_path'       : config.get(machine, 'VMPath'),
            'vmchecker_root' : vmcheckerpaths.root,
            'jobs_path'      : 'executor_jobs/',
            'scripts_path'   : 'executor_scripts/'},
        'guest' : {
            'username'  : config.get(machine, 'GuestUser'),
            'password'  : config.get(machine, 'GuestPassword'),
            'shell'     : config.get(machine, 'GuestShellPath'),
            'root_path' : {
                'native_style' : config.get(machine, 'GuestBasePath'),
                'shell_style'  : config.get(machine, 'GuestHomeInBash'),
                'separator'    : '/',
                },
            },
        'test'  : {
            0 : {
                'input'  : ['file.zip', 'tests.zip'],
                'script' : ['vmchecker_build.sh'],
                'output' : ['job_build'],
                'timeout': int(timeout),
                },
            1  : {
                'input'  : [],
                'script' : ['vmchecker_run.sh'],
                'output' : ['job_run', 'job_errors'],
                'timeout': int(timeout)
                }
            }
        }
    with open(dst_file, 'w') as f:
        f.write ('test='+str(test))



def _run_executor(ejobs, machine, assignment, timeout, kernel_messages):
    """Starts a job.

    XXX lots of wtf per minute
    XXX parsing config should be executors' job

    """
    dst_file = 'input_config.py'
    _make_test_config(ejobs, machine, timeout, kernel_messages, dst_file)
    args = [vmcheckerpaths.abspath('bin/vm_executor.py'), dst_file]
    _logger.info('Begin homework evaluation')
    _logger.debug('calling %s', args)

    start = time.time()

    # first just try to open the process
    try:
        popen = Popen(args)
    except Exception:
        _logger.exception('Cannot invoke VMExecutor.')
        with open(join(ejobs, 'job_errors'), 'a') as handler:
            print >> handler, 'Cannot run VMExecutor.'
            print >> handler, 'Please contact the administrators.'
        # if we cannot open the process, there is nothing more to be done
        return

    # waits for the the process to finish
    try:
        counter = 0
        deadline = start + int(timeout) + _EXECUTOR_OVERHEAD

        while time.time() < deadline:
            counter += 1
            exit_code = popen.poll()

            if exit_code is None:
                # if process has not finished => continue to sleep
                _logger.debug('-- VMExecutor sleeping for 5 seconds, '
                              'exit_code is None: x=%d', counter)
                # polls every 5 seconds
                time.sleep(5)
            else:
                with open(join(ejobs, 'job_errors'), 'a') as handler:
                    print >> handler, 'VMExecutor returned %d (%s)' % (
                        exit_code, ['success', 'error'][exit_code < 0])

                # no reason to stay in the loop after process exit terminates
                popen = None
                return
        else:
            _logger.error("VMChecker timeouted on assignment `%s' "
                          "running on machine `%s'.", assignment, machine)

            with open(join(ejobs, 'job_errors'), 'a') as handler:
                print >> handler, """\
VMExecutor successfuly started, but it's taking too long.
Check your sources, makefiles, etc and resubmit.
If the problem persists please contact administrators."""
    except:
        _logger.exception('Exception after starting VMExecutor.')

        with open(join(ejobs, 'job_errors'), 'a') as handler:
            print >> handler, """\
Error after starting VMExecutor.
If the problem persists please contact administrators."""
    finally:
        # release any leftover resources
        try:
            if popen:
                popen.kill()
        except:
            pass


def main(dir):
    """Unpacks archive and invokes executor"""
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

    assignment = config.get('Assignment', 'Assignment')  # yet another hack
    section = assignments._SECTION_PREFIX + assignment

    machine = storer.get(section, 'Machine')
    timeout = storer.get(section, 'Timeout')
    kernel_messages = storer.get(section, 'KernelMessages')

    _run_executor(ejobs, machine, assignment, timeout, kernel_messages)

    try:
        _run_callback(dir, ejobs)
    except:
        _logger.exception('cannot run callback')

    # clears files
    shutil.rmtree(ejobs)

    _logger.info('all done')


def _print_help():
    print >> sys.stderr, """Usage:
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
    config.config_tester()
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Invalid number of arguments.'
        _print_help()
        exit(1)

    start_dir = sys.argv[1]
    if not os.path.isdir(start_dir):
        print >> sys.stderr, 'Not a directory', start_dir
        _print_help()
        exit(1)
    _check_required_files(start_dir)
    main(start_dir)
