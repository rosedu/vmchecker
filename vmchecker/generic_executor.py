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
import shlex
from threading import Thread
from subprocess import Popen, PIPE, STDOUT

from vmchecker.config import VirtualMachineConfig

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

    def getVM(self, bundle_dir, sb_cfg):
        vm = VM(self, bundle_dir, sb_cfg)
        return None
	
    def start_host_commands(self, jobs_path, host_commands):
        """Run a set of commands on the tester (host) machine"""
        host_command_data = []

        for host_command_out in host_commands:
            out_file = 'run-km.vmr' # Default file name
            if host_command_out.rfind('>') != -1:
                out_file = host_command_out.split('>')[1].strip()

            host_command = host_command_out.split('>')[0].strip()

            if len(host_command) == 0:
                continue

            _logger.info('%%% -- starting host commands [' + host_command + '] >> ' + out_file)

            outf = open(os.path.join(jobs_path, out_file), 'a', buffering = 0)
            try:
                proc = Popen("exec " + host_command, stdout=outf, cwd = jobs_path, \
                    stderr = STDOUT, close_fds = True, shell = True, bufsize = 0)
            except:
                _logger.exception('HOSTPROC: opening process: ' + host_command)

            host_command_data.append((proc, outf))

        if len(host_command_data) == 0:
            return None
        return host_command_data

    def stop_host_commands(self, host_commands_data):
        """Stop previously run host commands"""
        if host_commands_data == None:
            return

        for host_command_data in host_commands_data:
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
    def __init__(self, host, bundle_dir, sb_cfg):
        self.host = host
        self.bundle_dir = bundle_dir
        self.sb_cfg = sb_cfg

        self.machinecfg = VirtualMachineConfig(sb_cfg, 'Machine')
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
        """Return False if an exception is thrown or the tests timeout."""
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

            return True
        except Exception as e:
            _logger.exception('Exception thrown in runTest(): ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())
            return False
        
    def try_power_on_vm_and_login(self, revertSnapshot=None):
        if revertSnapshot == True or \
           (revertSnapshot == None and self.sb_cfg.get('Assignment', 'RevertToSnapshot')):
            self.revert()

        self.start()
        return True
