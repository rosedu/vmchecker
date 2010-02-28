#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""An useful script for mass homeworks resubmition"""


import config
import submit
import repo_walker


class Resubmit(repo_walker.RepoWalker):
    def __init__(self, vmcfg):
        RepoWalker(self)
        self.vmcfg = vmcfg

    def resubmit(self, options):
        def _submit(assignment, user, location):
            """Submits assignment from `location'"""
            submit.send_submission(location)
        self.walk(vmcfg, options, _submit)


if __name__ == '__main__':
    vmcfg = config.config_storer()
    r = Resubmit(vmcfg)
    r.resubmit(config.options)
