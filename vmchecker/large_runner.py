#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vmchecker.generic_runner import Runner

class LargeRunner(Runner):
    def testSubmission(bundleDir):
        timeout = self.asscfg.get(self.assignment, 'Timeout')
        testcfg = {
            'input'  : ['tests.zip'],
            'script' : ['run.sh'],
            'output' : ['run-stdout.vmr', 'run-stderr.vmr'],
            'timeout': int(timeout)
            }

        super(LargeRunner, self).testSubmission(bundleDir, testcfg)

def get_runner(*args):
    return LargeRunner(*args)
