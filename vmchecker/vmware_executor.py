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


import pyvix.vix
from pyvix.vix import *
import os
import sys
import time
import logging
import signal
from threading import Thread
from subprocess import Popen
from vmchecker.generic_executor import VM, Host
from vmchecker.config import Config, AssignmentConfig, TesterConfig, VmwareMachineConfig, VmwareConfig

_logger = logging.getLogger('vm_executor')


class VmWareHost(Host):
    def getVM(self, bundle_dir, sb_cfg):
        return VmWareVM(self, bundle_dir, sb_cfg)

class VmWareVM(VM):
    vmhost = None
    vminstance = None
            
    def __init__(self, host, bundle_dir, sb_cfg):
        VM.__init__(self, host, bundle_dir, sb_cfg)
        self.machinecfg = VmwareMachineConfig(sb_cfg, 'Machine')
        self.vmwarecfg = VmwareConfig(sb_cfg, 'Tester')
        self.asscfg = AssignmentConfig(config = sb_cfg)
        self.testercfg = TesterConfig(config = sb_cfg)
        self.vmx_path = self.machinecfg.get_vmx_path()
        if self.vmx_path == None:
            self.vmx_path = self.get_submission_vmx_file()
        if self.vmx_path == None:
            # no vmx, nothing to do.
            _logger.error('Could not find a vmx to run')
            with open(self.error_fname, 'a') as handler:
                print >> handler, 'Error powering on the virtual machine.\n' + \
                                  'Unable to find .vmx file.\n'
            sys.exit(1)

        vmx_prefix = self.testercfg.vm_store_path('Tester')
        if vmx_prefix is not None:
            self.vmx_path = os.path.join(vmx_prefix, self.vmx_path)

        try:
            if self.vmwarecfg.vmware_type() == 3:
                self.vmhost = pyvix.vix.Host()
            elif self.vmwarecfg.vmware_type() == 2 or \
                    self.vmwarecfg.vmware_type() == 10:
                self.vmhost = pyvix.vix.Host(self.vmwarecfg.vmware_type(),
                                  self.vmwarecfg.vmware_url(),
                                  int(self.vmwarecfg.vmware_port()),
                                  self.vmwarecfg.vmware_username(),
                                  self.vmwarecfg.vmware_password())
        except pyvix.vix.VIXException:
            _logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())
            with open(self.error_fname, 'a') as handler:
                print >> handler, 'Error powering on the virtual machine.\n' + \
                                  'Connecting to the host Vmware services failed.\n'
            sys.exit(1)

        if self.vmwarecfg.vmware_register_and_unregister():
            self.vmhost.registerVM(self.vmwarecfg.vmware_rel_vmx_path(self.vmx_path))

        vmx_path = self.vmx_path
        if not os.path.isfile(vmx_path):
            vmx_path = self.vmwarecfg.vmware_rel_vmx_path(self.vmx_path)

        if not os.path.isfile(vmx_path):
            # no vmx, nothing to do.
            _logger.error('Could not find a vmx to run')
            with open(self.error_fname, 'a') as handler:
                print >> handler, 'Error powering on the virtual machine.\n' + \
                                  'Unable to find .vmx file.\n'
            sys.exit(1)

        try:
            self.vminstance = self.vmhost.openVM(vmx_path)
        except pyvix.vix.VIXException:
            _logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())
            with open(self.error_fname, 'a') as handler:
                print >> handler, 'Error powering on the virtual machine.\n' + \
                                  'Unable to open the .vmx file..\n'
            sys.exit(1)



    def executeCommand(self,cmd):
        return self.vminstance.runProgramInGuest(self.shell,'--login -c "'+cmd+'"')
    
    def start(self):
        self.vminstance.powerOn()

    def stop(self):
        try:
            self.vminstance.powerOff()
        except pyvix.vix.VIXException:
            _logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())
        if self.vmwarecfg.vmware_register_and_unregister():
            try:
                self.vmhost.unregisterVM(self.vmwarecfg.vmware_rel_vmx_path(self.vmx_path))
            except pyvix.vix.VIXException:
                _logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())

    def _wait_for_tools(self):
        """Called by the thread that waits for the VMWare Tools to
           start. If the Tools do not start, there is no direct way of
           ending the Thread.  As a result, on powerOff(), the Thread
           would throw a VIXException on account of the VM not being
           powered on.
        """
        try:
            self.vminstance.waitForToolsInGuest()
        except pyvix.vix.VIXException:
            _logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())


    def wait_for_tools_with_timeout(self, timeout, error_fname):
        """Wait for VMWare Tools to start.

        Returns True on success and False when the VMWare tools did not
        start properly in the given timeout. Writes error messages to
        `error_fname`.
        """

        if timeout > 0:
            _logger.info('Waiting for VMWare Tools with a timeout of %d seconds' % timeout)

        tools_thd = Thread(target = self._wait_for_tools)
        tools_thd.start()
        # normally the thread will end before the timeout expires, so a high timeout
        tools_thd.join(timeout)


        if not tools_thd.isAlive():
            return True


        _logger.error('Timeout waiting for VMWare Tools to start.' +
                      'Make sure your virtual machine boots up corectly' +
                      'and that you have VMWare Tools installed.')

        with open(error_fname, 'a') as handler:
            print >> handler, 'Timeout waiting for VMWare Tools to start.\n' + \
                      'Make sure your virtual machine boots up corectly\n' + \
                      'and that you have VMWare Tools installed.\n'
        return False

    def powerOn(self):
        """ see power_on_with_message_handler """
        power_thd = Thread(target = self.start)
        power_thd.start()
        power_thd.join(5)

        if not power_thd.isAlive():
            # vm.powerOn() didn't hang: the machine has been powered on
            return
        
        if self.vmwarecfg.vmware_type() == 2 or \
                self.vmwarecfg.vmware_type() == 10:
            proc = Popen(['vmchecker-message-handler',
                      self.vmwarecfg.vmware_hostname(),
                      self.vmwarecfg.vmware_username(),
                      self.vmwarecfg.vmware_password(),
                      self.vmwarecfg.vmware_rel_vmx_path(self.vmx_path)])
            os.waitpid(proc.pid, 0)
        
            power_thd.join()
        else:
            _logger.error('Powering on VM timed out')
            with open(self.error_fname, 'a') as handler:
                print >> handler, 'Error powering on the virtual machine.\n' + \
                                  'Timed out while powering on.\n'
            sys.exit(1)

    def try_power_on_vm_and_login(self, revertSnapshot=None):
        if revertSnapshot == True or \
           (revertSnapshot == None and self.asscfg.revert_to_snapshot('Assignment')):
            self.revert(self.vminstance.nRootSnapshots - 1)

        tools_timeout = self.asscfg.delay_wait_for_tools('Assignment')
        self.powerOn()
        
        if not self.wait_for_tools_with_timeout(tools_timeout, self.error_fname):
            # no tools, nothing to do.
            return False

        try:
            self.vminstance.loginInGuest(self.machinecfg.guest_user(), self.machinecfg.guest_pass())
        except pyvix.vix.VIXSecurityException:
            _logger.error('Error logging in on the virtual machine.' +
                          'Make sure you have the accounts properly configured.')
            with open(error_fname, 'a') as handler:
                print >> handler,'Error logging in on the virtual machine.\n' + \
                        'Make sure you have the user accounts properly configured.\n'
                return False

        time.sleep(self.asscfg.delay_between_tools_and_tests('Assignment'))
        return True
        
        
    def revert(self, number = None):
        """Revert the vminstance to the number snapshot

        Note: snapshots are counted from 0.
        """
        if number==None:
            _logger.error('Snapshot number is needed')
            return
        if self.vminstance.nRootSnapshots <= number:
            err_str = ('Cannot revert to snapshot %d. Too few ' +
                       'snapshots (nr = %d) found on %s.' %
                       (number, self.vminstance.nRootSnapshots, self.vminstance.vmxPath))
            raise Exception(err_str)
        snaps = self.vminstance.rootSnapshots
	try:
	        self.vminstance.revertToSnapshot(snaps[number])
	except:
	        _logger.error('Could not revert to snapshot')
       
    def copyTo(self, sourceDir, targetDir, files):
        """ Copy files from host(source) to guest(target) """
        for f in files:
            host_path = os.path.join(sourceDir, f)
            guest_path = targetDir + f
            if not os.path.exists(host_path):
                _logger.error('host file (to send) "%s" does not exist' % host_path)
                return
            _logger.info('copy file %s from host to guest at %s' % (host_path, guest_path))
            self.vminstance.copyFileFromHostToGuest(host_path, guest_path)
        
    def copyFrom(self, sourceDir, targetDir, files):
        """ Copy files from guest(source) to host(target) """
        for f in files:
            host_path = os.path.join(targetDir, f)
            guest_path = sourceDir + f
            _logger.info('copy file %s from guest to host at %s' % (guest_path, host_path))
            self.vminstance.copyFileFromGuestToHost(guest_path, host_path)
            if not os.path.exists(host_path):
                _logger.error('host file (received) "%s" does not exist' % host_path)

    def run(self, shell, executable_file, timeout):
        args = ' --login -c ' + '"chmod +x ' + executable_file + '; ' + executable_file + '"'
        self.executeCommand("chmod +x "+ executable_file)
        _logger.info('executing on the remote: prog=%s args=[%s] timeout=%d' % (shell, executable_file, timeout))
        thd = Thread(target = self.vminstance.runProgramInGuest, args = (shell,args))
        thd.start()
        thd.join(timeout)
        return thd.isAlive()
        
    def get_submission_vmx_file(self):
        """Unzip search the bundle_dir and locate the .vmx file, no matter
        in what sub-folders it is located in. If the unzipped archive has
        multiple .vmx files, just pick the first.

        """
        for (root, _, files) in os.walk(self.bundle_dir):
            for f in files:
                if f.endswith(".vmx"):
                    return os.path.join(root, f)
        return None

    def hasStarted(self):
        return self.vminstance[VIX_PROPERTY_VM_POWER_STATE] & VIX_POWERSTATE_TOOLS_RUNNING != 0

    def hasStopped(self):
        return self.vminstance[VIX_PROPERTY_VM_POWER_STATE] & VIX_POWERSTATE_POWERED_OFF != 0
