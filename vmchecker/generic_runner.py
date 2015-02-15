#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vmchecker.config import VirtualMachineConfig
import sys
import logging

class Runner():

    def __init__(self, host, vm):
        self.host = host
        self.vm = vm
        self.bundle_dir = vm.bundle_dir
        self.sb_cfg = vm.sb_cfg
        self.logger = logging.getLogger('vm_executor.' + self.__class__.__name__)


        self.machine = self.sb_cfg.get('Assignment', 'Machine')
        self.machinecfg = VirtualMachineConfig(self.sb_cfg, 'Machine')

    def testSubmission(self, bundleDir, buildCfg = None):
        # start host kernel message intercepting commands (including boot-up)
        kernel_messages = self.sb_cfg.get('Machine', 'KernelMessages', default='')
        kernel_messages_data = self.host.start_host_commands(self.bundle_dir, kernel_messages)

        success = self.vm.try_power_on_vm_and_login()
        if not success:
            self.logger.error('Could not power on or login on the VM')
            self.vm.stop()
            sys.exit(1)

        # start host commands
        host_command = self.sb_cfg.get('Machine', 'HostCommand', default='')
        host_command_data = self.host.start_host_commands(self.bundle_dir, host_command)
        
        timeout = self.sb_cfg.get('Assignment', 'Timeout')
        try:
            if buildCfg==None:
                buildcfg = {
                    'input'  : ['archive.zip', 'tests.zip'],
                    'script' : ['build.sh'],
                    'output' : ['build-stdout.vmr', 'build-stderr.vmr'],
                    'timeout': int(timeout),
                    }
                if not self.vm.runTest(self.bundle_dir, self.machinecfg, buildcfg):
                    self.logger.info('Build failed')
                    return
            
                testcfg = {
                    'input'  : [],
                    'script' : ['run.sh'],
                    'output' : ['run-stdout.vmr', 'run-stderr.vmr'],
                    'timeout': int(timeout)
                    }
                self.vm.runTest(self.bundle_dir, self.machinecfg, testcfg) 
            else:
                self.vm.runTest(self.bundle_dir, self.machinecfg, buildCfg)
        except Exception as e:
            self.logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())
        finally:
            self.host.stop_host_commands(kernel_messages_data)
            self.host.stop_host_commands(host_command_data)
            self.vm.stop()

