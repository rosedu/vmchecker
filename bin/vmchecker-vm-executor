#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

from pyvix.vix import *
import optparse
import os
import json
import logging
from threading import Thread
import sys

import vmcheckerpaths
import config

_logger = logging.getLogger('vm_executor')


def start_kernel_listener(args):
    _logger.info('started kernel listener')


def start_kernel_listener(args):
    _logger.info('stopped kernel listener')


def connectToVM(vmx_path):
    """Connect to the VmWare virtual machine specified by the vmx_path.

    Returns a pair: (a handle for the connection to the host, a virtual machine handle)"""
    h = Host()
    vm = h.openVM(vmx_path)
    return (h, vm)


def revertToSnapshot(vm, snapNr):
    """Revert the vm to the snapNr snapshot

    Note: snapshots are counted from 0.
    """
    if vm.nRootSnapshots <= snapNr:
        err_str = ('Cannot revert to snapshot %d. Too few snapshots (nr = %d) found on %s.' %
                   (snapNr, vm.nRootSnapshots, vm.vmxPath))
        raise Exception(err_str)
    snaps = vm.rootSnapshots
    vm.revertToSnapshot(snaps[snapNr])


def copyFilesBetweenHostAndGuest(vm, fromHostToGuest, host_dir, guest_dir, files):
    """Copy files from the host to the guest.
    vm        - an open virtual machine.
    host_dir  - the directory on the host
    guest_dir - an ABSOLUTE path to the guest directory
                This must be expressed in the native system's path style.
                For example if the system is Windows and you have installed
                cygwin, you cannot use cygwin-like paths.
                This myst end with a GUEST speciffic path separator
                (e.g.: bad: 'C:\dir'
                      good: 'C:\dir\')
    files     - the list of files (relative to host_dir) to copy to the vm.
    """

    for f in files:
        host_path = os.path.join(host_dir, f)
        # NOTE: os.path.join() is not good for guest_path because the
        #  guest might be on a different platform with different path
        #  separators. Because of this the guest_dir MUST terminate
        #  with the guest-speciffic path separator!
        guest_path = guest_dir + f
        if fromHostToGuest:
            _logger.info('copy file %s from host to guest at %s' % (host_path, guest_path))
            vm.copyFileFromHostToGuest(host_path, guest_path)
        else:
            _logger.info('copy file %s from guest to host at %s' % (guest_path, host_path))
            vm.copyFileFromGuestToHost(guest_path, host_path)



def copyFilesFromGuestToHost(vm, host_dir, guest_dir, files):
    """see copyFilesBetweenHostAndGuest"""
    return copyFilesBetweenHostAndGuest(vm, False, host_dir, guest_dir, files)


def copyFilesFromHostToGuest(vm, host_dir, guest_dir, files):
    """see copyFilesBetweenHostAndGuest"""
    return copyFilesBetweenHostAndGuest(vm, True, host_dir, guest_dir, files)


def makeExecutableAndRun(vm, guest_shell, executable_file, timeout):
    """Make a guest file executables and execute it.

    Copying a file to the vm will not necesarily make it executable
    (on UNIX systems). Therefore we must first make it executable
    (chmod) and then run it. This will be done on Windows systems also
    because we run this in cygwin (for the time being).

    The guest_shell must be specified in a native path style:
      - c:\cygwin\bin\bash.exe - on windows
      - /bin/bash - on UNIX.

    This is needed because vmware tools uses native paths and system
    calls to execute files.

    The executable_file path must the path in the shell for that file.
    """
    args = ' --login -c ' + '"chmod +x ' + executable_file + '; ' + executable_file + '"'
    return runWithTimeout(vm, guest_shell, args, timeout)


def runWithTimeout(vm, prog, args, timeout):
    """ Runs the 'prog' program with 'args' arguments in the 'vm'
    virtual machine instance (assumming it's running correctly).

    Returns True if the thread terminated it's execution withing
    'timeout' seconds (or fractions thereof) and False otherwise.

    """
    class RunInThread(Thread):
        def __init__(self, vm, prog, args):
            Thread.__init__(self)
            self.vm = vm
            self.prog = prog
            self.args = args
        def run(self):
            self.vm.runProgramInGuest(self.prog, self.args)

    try:
        _logger.info('executing on the remote: prog=%s args=[%s] timeout=%d' %
                     (prog, args, timeout))
        thd = RunInThread(vm, prog, args)
        thd.start()
        thd.join(timeout)
        return thd.isAlive()
    except Exception:
        return False


def _run_a_test(vm, jobs_path, scripts_path, guest, test):
    """Run a test:
       * copy input files to guest
       * copy script files to guest
       * make scripts executable (Linux)
       * execute scripts
       * copy output files from guest

       If at any errors occur, return False.
       On success, return True.
    """
    try:
        copyFilesFromHostToGuest(vm, jobs_path,    guest['root_path']['native_style'], test['input'])
        copyFilesFromHostToGuest(vm, scripts_path, guest['root_path']['native_style'], test['script'])
        for script in test['script']:
            timedout = makeExecutableAndRun(vm, guest['shell'], guest['root_path']['shell_style'] + guest['root_path']['separator'] + script, test['timeout'])
            if timedout:
                return False
        copyFilesFromGuestToHost(vm, jobs_path,    guest['root_path']['native_style'], test['output'])
    finally:
        return True


def main(args):
    _logger.info(args)
    host  = args['host']
    guest = args['guest']
    jobs_path    = os.path.join(host['vmchecker_root'], host['jobs_path'])
    scripts_path = os.path.join(host['vmchecker_root'], host['scripts_path'])

    (h, vm) = connectToVM(host['vmx_path'])
    revertToSnapshot(vm, 0)
    vm.loginInGuest(guest['username'], guest['password'])

    if args['km_enable']:
        start_kernel_listener(args)

    tests = args['test']
    for i in tests:
        success = _run_a_test(vm, jobs_path, scripts_path, guest, tests[i])
        if not success:
            break # stop running tests if an error occured.

    if args['km_enable']:
        stop_kernel_listener(args)


_default_test = {
    'km_enable' : False,
    'host' : {
        'vmx_path'       : '/home/so/vmware/so-vm-debian-sid/faust.vmx',
        'vmchecker_root' : '/home/lucian/vmchecker/vmchecker/',
        'jobs_path'      : 'executor_jobs/',
        'scripts_path'   : 'executor_scripts/'},
    'guest' : {
        'username'  : 'so',
        'password'  : 'so',
        'shell'     : '/bin/bash',
        'root_path' : {
            'native_style' : '/home/so/',
            'shell_style'  : '/home/so/',
            'separator'    : '/',
            },
        },
    'test'  : {
        0 : {
            'input'  : ['file.zip', 'tests.zip'],
            'script' : ['vmchecker_build.sh'],
            'output' : ['job_build'],
            'timeout': 120
            },
        1  : {
            'input'  : [],
            'script' : ['vmchecker_run.sh'],
            'output' : ['job_run', 'job_errors'],
            'timeout': 120
            }
        }
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # if no args specified run a default test
    test = _default_test
    if len(sys.argv) != 1:
        testcfg_file = sys.argv[1]
        try:
            # the first arg should be a python file which defines a
            # dictioary named test. The format of the dictionary is
            # the same as the one above.
            with open(testcfg_file, 'r') as handler:
                test = json.load(handler)
        except:
            _logger.error('could not load %s ' % modname)

    # run the test :)
    main(test)

    # some vmware calls may block indefinetly.  if we don't exit
    # explicitly, we may never return (this is due to python waiting
    # for all threads to exit, but some threads may be stuck in a
    # blocking vmware vix call.
    sys.exit(0)
