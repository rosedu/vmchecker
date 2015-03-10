#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vmchecker.generic_runner import Runner
from threading import Thread
import time

class OneRebootRunner(Runner):
    def _wait_for_power_off(self):
        while self.vm.hasStopped() != True:
            time.sleep(1)
            
    def testSubmission(self, bundleDir):
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
            buildcfg = {
                'input'  : ['archive.zip', 'tests.zip'],
                'script' : ['build.sh'],
                'output' : ['build-stdout.vmr', 'build-stderr.vmr'],
                'timeout': int(timeout),
                }
            if not self.vm.runTest(self.bundle_dir, self.machinecfg, buildcfg):
                self.logger.info('Build failed')
                return

            self.vm.stop()
            self.logger.info('Waiting for VM to power off.')
            thd = Thread(target = self._wait_for_power_off)
            thd.start()
            thd.join()

            success = self.vm.try_power_on_vm_and_login(False)
            if not success:
                self.logger.error('Could not power on or login on the VM')
                self.vm.stop()
                sys.exit(1)
       
            testcfg = {
                'input'  : [],
                'script' : ['run.sh'],
                'output' : ['run-stdout.vmr', 'run-stderr.vmr'],
                'timeout': int(timeout)
                }
            self.vm.runTest(self.bundle_dir, self.machinecfg, testcfg) 
        except Exception as e:
            self.logger.exception('Exception thrown: ' + type(e).__name__ + "\n" + ", ".join(e.args) + "\n" + e.__str__())
        finally:
            self.host.stop_host_commands(kernel_messages_data)
            self.host.stop_host_commands(host_command_data)
            self.vm.stop()

def get_runner(*args):
    return OneRebootRunner(*args)
