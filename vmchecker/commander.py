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

# Use simplejson or Python 2.6 json, prefer simplejson.
try:
    import simplejson as json
except ImportError:
    import json


import ConfigParser
import time
import sys
import os
from subprocess import Popen

from . import callback
from . import vmlogging
from .paths import submission_config_file

_logger = vmlogging.create_module_logger('commander')

_FILES_TO_SEND = (
    'vmchecker-stderr.vmr',
    'build-stdout.vmr',
    'build-stderr.vmr',
    'run-stdout.vmr',
    'run-stderr.vmr',
    'run-km.vmr',
    'grade.vmr',)
_EXECUTOR_OVERHEAD = 300



def _run_callback(bundle_dir):
    """Runs callback script to upload results"""
    abs_files = (os.path.join(bundle_dir, f) for f in _FILES_TO_SEND)
    callback.run_callback(submission_config_file(bundle_dir), abs_files)





def _run_executor(json_cfg_fname, executor_job_dir, assignment, timeout):
    """Starts a job.

    Allthough it would be nicer to import vm-executor and just invoke
    methods from there, the vm-executor can get stuck (due to fauly
    pyvix interaction with the vmware server 1 daemon). We're already
    called directly from queue-manager. If we get stuck too, the whole
    tester-side vmchecker gets stuck.

    Because of this, vm-executor is launched in a separate process.
    """

    # get the current time
    start = time.time()
    deadline = start + int(timeout) + _EXECUTOR_OVERHEAD


    # first just try to open the process
    try:
        cmd = ['vmchecker-vm-executor', json_cfg_fname]
        _logger.info('Begin homework evaluation. Calling %s', cmd)

        popen = Popen(cmd)

        with open(os.path.join(executor_job_dir, 'grade.vmr'), 'w') as handler:
            print >> handler, 'ok'
    except OSError:
        _logger.exception('Cannot invoke VMExecutor.')
        with open(os.path.join(executor_job_dir, 'vmchecker-stderr.vmr'), 'a') as handler:
            print >> handler, 'Cannot run VMExecutor.'
            print >> handler, 'Please contact the administrators.'
        # if we cannot open the process, there is nothing more to be done
        return




    # waits for the the process to finish
    try:
        counter = 0
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
                with open(os.path.join(executor_job_dir, 'vmchecker-stderr.vmr'), 'a') as handler:
                    print >> handler, 'VMExecutor returned %d (%s)' % (
                        exit_code, ['success', 'error'][exit_code < 0])

                # no reason to stay in the loop after process exit terminates
                popen = None
                return
        else:
            _logger.error("VMChecker timeouted on assignment `%s'" % assignment)
            with open(os.path.join(executor_job_dir, 'vmchecker-stderr.vmr'), 'a') as handler:
                print >> handler, """\ VMExecutor successfuly started,
                      but it's taking too long. Check your sources,
                      makefiles, etc and resubmit.  If the problem
                      persists please contact administrators."""
    except:
        _logger.exception('Exception after starting VMExecutor.')
        with open(os.path.join(executor_job_dir, 'vmchecker-stderr.vmr'), 'a') as handler:
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
            _logger.exception('Nested exception in kill(PID=%d)', popen.pid)




def _check_required_files(path):
    """Checks that a set of files required by commander is present in
    the given path."""
    found_all = True
    needed_files = ['archive.zip', 'tests.zip', 'submission-config']
    found_files = os.listdir(path)
    not_found = []
    for need in needed_files:
        if not need in found_files:
            _logger.error('Could not find necessary file [%s] in [%s]' % (
                    need, path))
            found_all = False
            not_found.append(need)
    if not found_all:
        raise IOError('Files ' + not_found + ' required for testing missing')



def _make_test_config(bundle_dir, assignment, vmcfg, asscfg):
    """Returns an object with a configuration suitable for
    vm-executor"""
    timeout = asscfg.get(assignment, 'Timeout')
    machine = asscfg.get(assignment, 'Machine')
    kernel_messages_str = asscfg.get(assignment, 'KernelMessages')

    kernel_messages = True if int(kernel_messages_str) != 0 else False
    return {
        'km_enable' : kernel_messages,
        'host' : {
            'vmx_path'       : vmcfg.get(machine, 'VMPath'),
            'vmchecker_root' : vmcfg.root_path(),
            'jobs_path'      : bundle_dir,
            'scripts_path'   : bundle_dir},
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
        'test'  : [
            {
                'input'  : ['archive.zip', 'tests.zip'],
                'script' : ['build.sh'],
                'output' : ['build-stdout.vmr', 'build-stderr.vmr'],
                'timeout': int(timeout),
                },
            {
                'input'  : [],
                'script' : ['run.sh'],
                'output' : ['run-stdout.vmr', 'run-stderr.vmr'],
                'timeout': int(timeout)
                }
            ]
        }


def _write_test_config(dst_file, bundle_dir, assignment, vmcfg, asscfg):
    """Write the test configuration to a json file to be passed in to
    the vm-executor"""
    with open(dst_file, 'w') as handler:
        testcfg = _make_test_config(bundle_dir, assignment, vmcfg, asscfg)
        testcfg_str = json.dumps(testcfg)
        handler.write(testcfg_str)


def _get_assignment_id(bundle_dir):
    """Reads the assignment identifier from the config file of the
    submission from bundle_dir"""
    with open(submission_config_file(bundle_dir)) as handle:
        config = ConfigParser.RawConfigParser()
        config.readfp(handle)
    assignment = config.get('Assignment', 'Assignment')
    return assignment



def prepare_env_and_test(vmcfg, bundle_dir):
    """Prepare testing environment for vm-executor, create a config
    file and run vm-executor"""

    _check_required_files(bundle_dir)

    assignment = _get_assignment_id(bundle_dir)
    asscfg  = vmcfg.assignments()
    timeout = asscfg.get(assignment, 'Timeout')


    json_cfg_fname = os.path.join(bundle_dir, 'vm_executor_config.json')
    _write_test_config(json_cfg_fname, bundle_dir, assignment, vmcfg, asscfg)

    try:
        _run_executor(json_cfg_fname, bundle_dir, assignment, timeout)
        _run_callback(bundle_dir)
    except:
        _logger.exception('cannot run callback')
    _logger.info('all done')


def _print_usage():
    """Prints a help string"""
    print >> sys.stderr, """Usage:
    ./commander.py course_id directory - where directory contains:
        `archive.zip' `tests.zip' `config'"""
