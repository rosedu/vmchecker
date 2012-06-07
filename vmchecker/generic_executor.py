#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A script that starts a vm, reverts it to a known snapshot, tests a
submission bundle (submission + tests), and closes the vm"""

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

from vmchecker.config import VmwareMachineConfig, CourseConfig, VmwareConfig

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

    def getVM(self, machinecfg):
        vm = VM(self, machinecfg)
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
    vmtype 	= None
    username	= None
    password	= None
    IP	= None
    cfg = None
    def __init__(self, host, machinecfg):
	    self.host = host
	    self.username = machinecfg.guest_user()
	    self.password = machinecfg.guest_pass()
	    self.cfg = machinecfg
	    # TODO check if path exists

    def executeCommand(self, cmd):
	    # host.executeCommand(...)
	    pass

    def executeNativeCommand(self, cmd):
	    # there is no default need for native commands
	    return self.executeCommand(cmd)

    def hasStarted(self):
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
        
    def run(self, executable_file, shell=None, timeout=None):
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
            
    def powerOn(self):
        """ see power_on_with_message_handler """
        power_thd = Thread(target = vm.start)
        power_thd.start()
        power_thd.join(5)

        if not power_thd.isAlive():
            # vm.powerOn() didn't hang: the machine has been powered on
            return
        else:
            _logger.error("Could not power on")

        power_thd.join()
        
    def try_power_on_vm_and_login(self, vmwarecfg, machinecfg, assignment, asscfg, bundle_dir, vmx_path):
        """Power on the virtual machine taking care of possbile messages
           and handle the case in which the virtual machine doesn't have
           VMWare Tools installed or the username and password given are
           wrong."""

        error_fname = os.path.join(bundle_dir, 'vmchecker-stderr.vmr')
        tools_timeout = asscfg.delay_wait_for_tools(assignment)

        if asscfg.revert_to_snapshot(assignment):
            self.revert()

        self.start()    
        time.sleep(asscfg.delay_between_tools_and_tests(assignment))
        return True
        
    def test_submission(self, bundle_dir, vmcfg, assignment):
        asscfg  = vmcfg.assignments()
        timeout = asscfg.get(assignment, 'Timeout')
        machine = asscfg.get(assignment, 'Machine')
        machinecfg = VmwareMachineConfig(vmcfg, machine)
        vmwarecfg = VmwareConfig(vmcfg.testers(), machinecfg.get_tester_id())
        error_fname = os.path.join(bundle_dir, 'vmchecker-stderr.vmr')
        
        vmx_path = machinecfg.get_vmx_path()
        success = self.try_power_on_vm_and_login(vmwarecfg, machinecfg, assignment,
                                            asscfg, bundle_dir, vmx_path)
        if not success:
            _logger.error('Could not power on or login on the VM')
            self.stop()
            sys.exit(1)


        # start host commands
        host_command = vmcfg.get(machine, 'HostCommand', default='')
        host_command_data = self.host.start_host_commands(bundle_dir, host_command)

        try:
            buildcfg = {
                'input'  : ['archive.zip', 'tests.zip'],
                'script' : ['build.sh'],
                'output' : ['build-stdout.vmr', 'build-stderr.vmr'],
                'timeout': int(timeout),
                }
            if not self.runTest(bundle_dir, machinecfg, buildcfg):
                _logger.info('Build failed')
                return
        
            testcfg = {
                'input'  : [],
                'script' : ['run.sh'],
                'output' : ['run-stdout.vmr', 'run-stderr.vmr'],
                'timeout': int(timeout)
                }
            self.runTest(bundle_dir, machinecfg, testcfg) 
        except Exception:
            _logger.exception('FUCK! Exception!RUUUUUUUN!!!')
        finally:
            self.host.stop_host_commands(host_command_data)
            self.stop()

