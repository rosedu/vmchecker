#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""An useful script for mass homeworks resubmition"""


import config
import submit
import repo_walker


def _submit(assignment, user, location):
    """Submits assignment from `location'"""
    submit.send_submission(location)


if __name__ == '__main__':
    vmcfg = config.config_storer()
    repo_walker.walk(vmcfg, _submit)
