#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Evaluates one homework.

Usage:
    ./commander.py directory - where directory contains (see submit.py)
        `archive.zip' `tests.zip' `config'


The script parses config and invokes vm_executor with
the requiered arguments.

VMExecutor excepts files in `executor_jobs' so it's not safe
to run two instances of commander simultaneously.

When done the vmchecker.callback module passing in files retrieved
from the vm or constructed on the commander.
"""

from __future__ import with_statement


import ConfigParser
import shutil
import time
import sys
import os
import json
from subprocess import Popen

from . import callback
from . import vmlogging
from .config import VmcheckerConfig
from .CourseList import CourseList


_logger = vmlogging.create_module_logger('commander')

_FILES_TO_SEND = (
    'job_build',
    'job_run',
    'job_errors',
    'job_results',
    'job_km', )
_EXECUTOR_OVERHEAD = 300



def _run_callback(bundle_dir):
    """Runs callback script to upload results"""
    abs_files = (os.path.join(bundle_dir, f) for f in _FILES_TO_SEND)
    callback.run_callback(os.path.join(bundle_dir, 'config'), abs_files)


def _make_test_config(vmcfg, assignment, bundle_dir):
    """Returns an object with a configuration suitable for
    vm-executor"""
    asscfg  = vmcfg.assignments()
    machine = asscfg.get(assignment, 'Machine')
    timeout = asscfg.get(assignment, 'Timeout')
    kernel_messages = asscfg.get(assignment, 'KernelMessages')

    km = True if int(kernel_messages) != 0 else False
    return {
        'km_enable' : km,
        'host' : {
            'vmx_path'       : vmcfg.get(machine, 'VMPath'),
            'vmchecker_root' : vmcfg.root_path(),
            'jobs_path'      : bundle_dir,
            'scripts_path'   : 'executor_scripts/'},
        'guest' : {
            'username'  : vmcfg.get(machine, 'GuestUser'),
            'password'  : vmcfg.get(machine, 'GuestPassword'),
            'shell'     : vmcfg.get(machine, 'GuestShellPath'),
            'root_path' : {
                'native_style' : vmcfg.get(machine, 'GuestBasePath'),
                'shell_style'  : vmcfg.get(machine, 'GuestHomeInBash'),
                'separator'    : '/',
                },
            },
        'test'  : {
            0 : {
                'input'  : ['archive.zip', 'tests.zip'],
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



def _run_executor(json_cfg_fname, executor_job_dir, assignment, timeout):
    """Starts a job.

    XXX lots of wtf per minute
    XXX parsing config should be executors' job

    """
    args = ['vmchecker-vm-executor', json_cfg_fname]
    _logger.info('Begin homework evaluation')
    _logger.debug('calling %s', args)

    start = time.time()

    # first just try to open the process
    try:
        popen = Popen(args)
    except OSError:
        _logger.exception('Cannot invoke VMExecutor.')
        with open(os.path.join(executor_job_dir, 'job_errors'), 'a') as handler:
            print >> handler, 'Cannot run VMExecutor.'
            print >> handler, 'Please contact the administrators.'
        # if we cannot open the process, there is nothing more to be done
        return

    with open(os.path.join(executor_job_dir, 'job_results'), 'w') as handler:
        print >> handler, 'ok'

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
                with open(os.path.join(executor_job_dir, 'job_errors'), 'a') as handler:
                    print >> handler, 'VMExecutor returned %d (%s)' % (
                        exit_code, ['success', 'error'][exit_code < 0])

                # no reason to stay in the loop after process exit terminates
                popen = None
                return
        else:
            _logger.error("VMChecker timeouted on assignment `%s'" % assignment)

            with open(os.path.join(executor_job_dir, 'job_errors'), 'a') as handler:
                print >> handler, """\ VMExecutor successfuly started,
                      but it's taking too long. Check your sources,
                      makefiles, etc and resubmit.  If the problem
                      persists please contact administrators."""
    except:
        _logger.exception('Exception after starting VMExecutor.')

        with open(os.path.join(executor_job_dir, 'job_errors'), 'a') as handler:
            print >> handler, """\ Error after starting VMExecutor.
                  If the problem persists please contact
                  administrators."""
    finally:
        # release any leftover resources
        try:
            if not popen is None:
                import signal
                os.kill(popen.pid, signal.SIGTERM)
                # can't do "popen.kill()" here because that's
                # python2.6 speciffic :(
        except:
            pass


def _check_required_files(path):
    """Checks that a set of files required by commander is present in
    the given path."""
    found_all = True
    needed_files = ['archive.zip', 'tests.zip', 'config']
    found_files = os.listdir(path)
    for need in needed_files:
        if not need in found_files:
            _logger.error('Could not find necessary file [%s] in [%s]' % (
                    need, path))
            found_all = False
    if not found_all:
        exit(-1)


def _write_test_config(dst_file, vmcfg, assignment, bundle_dir):
    """Write the test configuration to a json file to be passed in to
    the vm-executor"""
    with open(dst_file, 'w') as handler:
        testcfg = _make_test_config(vmcfg, assignment, bundle_dir)
        testcfg_str = json.write(testcfg)
        handler.write(testcfg_str)


def _get_assignment_id(bundle_dir):
    """Reads the assignment identifier from the config file of the
    submission from bundle_dir"""
    with open(os.path.join(bundle_dir, 'config')) as handle:
        config = ConfigParser.RawConfigParser()
        config.readfp(handle)
    assignment = config.get('Assignment', 'Assignment')  # yet another hack
    return assignment

def prepare_env_and_test(vmcfg, bundle_dir):
    """Prepare testing environment for vm-executor, create a config
    file and run vm-executor"""

    _check_required_files(bundle_dir)
    assignment = _get_assignment_id(bundle_dir)

    json_cfg_fname = os.path.join(bundle_dir, 'vm_executor_config.json')
    _write_test_config(json_cfg_fname, assignment, bundle_dir, vmcfg)

    try:
        _run_executor(json_cfg_fname, bundle_dir, assignment, timeout)
        _run_callback(bundle_dir)
    except:
        _logger.exception('cannot run callback')

    # clears files
    shutil.rmtree(bundle_dir)

    _logger.info('all done')


def _print_usage():
    """Prints a help string"""
    print >> sys.stderr, """Usage:
    ./commander.py course_id directory - where directory contains:
        `archive.zip' `tests.zip' `config'"""


def main():
    """Invokes executor with parameters from the command line"""
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Invalid number of arguments.'
        _print_usage()
        exit(1)

    course_id = sys.argv[1]
    bundle_dir = sys.argv[2]
    if not os.path.isdir(bundle_dir):
        print >> sys.stderr, 'Not a directory', bundle_dir
        _print_usage()
        exit(1)

    vmcfg = VmcheckerConfig(CourseList().course_config(course_id))
    prepare_env_and_test(vmcfg, bundle_dir)


if __name__ == '__main__':
    main()
