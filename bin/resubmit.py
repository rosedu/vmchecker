#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""An useful script for mass homeworks resubmition"""


import config
import submit
import repo_walker


def _submit(assignment, user, location):
    """Submits assignment from `location'"""
    submit.submit_homework(location)


if __name__ == '__main__':
    config.config_storer()
    repo_walker.walk(_submit)
