#! /usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import os

import submit
import repo_walker


def _submit(assignment, user, location):
    submit.submit_assignment(os.path.join(location, 'config'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    repo_walker.parse_arguments()
    repo_walker.walk(_submit)
