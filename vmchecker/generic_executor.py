#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The definition of the base classes Host and VM which
provide the necessary primitives to interact with a vm and
test a submission bundle."""

from __future__ import with_statement


# Use simplejson or Python 2.6 json, prefer simplejson.
try:
    import simplejson as json
except ImportError:
    import json

import os
import sys
import time
import logging
import signal
import ConfigParser
import shlex
from threading import Thread
from subprocess import Popen, PIPE, STDOUT

from vmchecker.config import VirtualMachineConfig, CourseConfig, VmwareConfig

_logger = logging.getLogger('vm_executor')



class Host():
    def __init__(self):
        pass

    def executeCommand(self, cmd):
        _logger.debug('Running command: %s' % cmd)
        p = Popen([cmd],stdout=PIPE,stderr=STDOUT,shell=True)
        output = p.stdout.read()
        _logger.debug('Command output: %s' % output)
        return output

    def getVM(self, bundle_dir, vmcfg, assignment):
        vm = VM(self, bundle_dir, vmcfg, assignment)
        return None
	
    def start_host_commands(self, jobs_path, host_command):
        """Run a command on the tester (host) machine"""
        _logger.info('%%% -- starting host commands [' + host_command + ']')

        if len(host_command) == 0:
            return None

        outf = open(os.path.join(jobs_path, 'run-km.vmr'), 'a')
        try:
            proc = Popen(host_command, stdout=outf, shell=True)
        except:
            _logger.exception('HOSTPROC: opening process: ' + host_command)
        return (proc, outf)
        
    def stop_host_commands(self, host_command_data):
        """Stop previously run host commands"""
        if host_command_data == None:
            return

        (proc, outf) = host_command_data
        try:
            os.kill(proc.pid, signal.SIGTERM)
            outf.close()
        except:
            _logger.exception('HOSTPROC: while stopping host cmds')
        _logger.info("%%% -- stopped host commands")
		    
class VM():
    host 	= None
    path 	= None
    username	= None
    password	= None
    IP	= None
    def __init__(self, host, bundle_dir, vmcfg, assignment):
        self.host = host
        self.bundle_dir = bundle_dir
        self.vmcfg = vmcfg
        self.assignment = assignment

        self.asscfg  = vmcfg.assignments()
        self.machine = self.asscfg.get(assignment, 'Machine')
        self.machinecfg = VirtualMachineConfig(vmcfg, self.machine)
        self.error_fname = os.path.join(bundle_dir, 'vmchecker-stderr.vmr')
        self.shell = self.machinecfg.guest_shell_path()

        self.username = self.machinecfg.guest_user()
        self.password = self.machinecfg.guest_pass()

    def executeCommand(self, cmd):
        # host.executeCommand(...)
        pass

    def executeNativeCommand(self, cmd):
        # there is no default need for native commands
        return self.executeCommand(cmd)

    def hasStarted(self):
        return False

    def hasStopped(self):
        return False

    def start(self):
        pass
        
    def stop(self):
        pass
        
    def revert(self, number = None):
        pass
        
    def copyTo(self, targetDir, sourceDir, files):
        pass

    def copyFrom(self, targetDir, sourceDir, files):
        pass
        
    def run(self, shell, executable_file, timeout):
        pass
        
    def runTest(self, bundle_dir, machinecfg, test):
        """ originally named  def copy_files_and_run_script(vm, bundle_dir, machinecfg, test) """
        try:
            files_to_copy = test['input'] + test['script']
            guest_dest_dir = machinecfg.guest_base_path()
            self.copyTo(bundle_dir,guest_dest_dir,files_to_copy)
            for script in test['script']:
                shell = machinecfg.guest_shell_path()
                dest_in_guest_shell = machinecfg.guest_home_in_shell()
                script_in_guest_shell = dest_in_guest_shell  + script
                timedout = self.run(shell,script_in_guest_shell,test['timeout'])
                self.copyFrom(guest_dest_dir,bundle_dir,test['output'])
                if timedout:
                    return False
        except:
            _logger.exception('error in copy_files_and_run_script')
        finally:
            return True
        
    def try_power_on_vm_and_login(self, revertSnapshot=None):
        if revertSnapshot == True or \
           (revertSnapshot == None and self.asscfg.revert_to_snapshot(self.assignment)):
            self.revert()

        self.start()
        return True
        
    def test_submission(self, buildcfg = None):
        # start host kernel message intercepting commands (including boot-up)
        kernel_messages = self.vmcfg.get(self.machine, 'KernelMessages', default='')
        kernel_messages_data = self.host.start_host_commands(self.bundle_dir, kernel_messages)

        success = self.try_power_on_vm_and_login()
        if not success:
            _logger.error('Could not power on or login on the VM')
            self.stop()
            sys.exit(1)

        # start host commands
        host_command = self.vmcfg.get(self.machine, 'HostCommand', default='')
        host_command_data = self.host.start_host_commands(self.bundle_dir, host_command)
        
        timeout = self.asscfg.get(self.assignment, 'Timeout')
        try:
            if buildcfg==None:
                buildcfg = {
                    'input'  : ['archive.zip', 'tests.zip'],
                    'script' : ['build.sh'],
                    'output' : ['build-stdout.vmr', 'build-stderr.vmr'],
                    'timeout': int(timeout),
                    }
                if not self.runTest(self.bundle_dir, self.machinecfg, buildcfg):
                    _logger.info('Build failed')
                    return
            
                testcfg = {
                    'input'  : [],
                    'script' : ['run.sh'],
                    'output' : ['run-stdout.vmr', 'run-stderr.vmr'],
                    'timeout': int(timeout)
                    }
                self.runTest(self.bundle_dir, self.machinecfg, testcfg) 
            else:
                self.runTest(self.bundle_dir, self.machinecfg, buildcfg)
        except Exception:
            _logger.exception('FUCK! Exception!RUUUUUUUN!!!')
        finally:
            self.host.stop_host_commands(host_command_data)
            self.host.stop_host_commands(kernel_messages_data)
            self.stop()

