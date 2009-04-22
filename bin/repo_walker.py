#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provides functionality to manipulate batches homeworks"""

from __future__ import with_statement

import optparse
import os
import sys
import logging
from os import path

import misc


_logger = logging.getLogger('repo_walker')
cmdline = optparse.OptionParser()   # XXX how about moving these to misc
options, args = None, None


cmdline.add_option('-r', '--recursive', action='store_true', dest='recursive',
                   default=False)
cmdline.add_option('-u', '--user', dest='user')
cmdline.add_option('-a', '--assignment', dest='assignment')
cmdline.add_option('-s', '--simulate', action='store_true', dest='simulate',
                   default=False)
cmdline.add_option('--all', action='store_true', dest='all',
                   default=False)

def parse_arguments():
    """Parses comandline arguments"""
    global options, args
    options, args = cmdline.parse_args()

    error = ''

    if (options.user is None
            and options.assignment is None
            and options.recursive == False
            and options.all == False):
        error = ('At least one of --user, --assignment, '
                 '--recusive, --all should be specified')

    if ((options.recursive or options.all)
            and (options.user is not None
                or options.assignment is not None)):
        error = ('Options --recursive and --all '
                 'are incompatible with --user and --assignment')

    if options.recursive and options.all:
        error = "You can't specify both --recursive and --all"

    if error:
        print error
        cmdline.print_help(file=sys.stdout)
        exit(1)


def walk(func, args=()):
    """Walks the repository and calls func for the homeworks found"""
    repo = misc.repository()

    for assignment in os.listdir(repo):
        assignment_path = path.join(repo, assignment)

        if not path.isdir(assignment_path):
            _logger.debug('Ignoring %s (not a directory)', assignment_path)
            continue

        # XXX maybe an 'assignment' module would be appropriate
        if assignment not in misc.config().sections():
            _logger.debug('Ignoring %s (not an assignment)', assignment_path)
            continue

        if options.assignment is not None and options.assignment != assignment:
            _logger.debug('Ignoring %s (as requested by --assignment)',
                          assignment_path)
            continue

        for user in os.listdir(assignment_path):
            user_path = path.join(assignment_path, user)

            if not path.isdir(user_path):
                _logger.debug('Ignoring %s (not a directory)', user_path)
                continue

            if not path.isfile(path.join(user_path, 'config')):
                _logger.debug('Ignoring %s (no config file)', user_path)
                continue

            if options.user is not None and options.user != user:
                _logger.debug('Ignoring %s (as requested by --user)', user_path)
                continue

            if options.recursive:
                if path.commonprefix((os.getcwd(), user_path)) != os.getcwd():
                    _logger.debug('Ignoring %s (in current directory)',
                                  user_path)
                    continue

            _logger.info('Walking on %s, %s (%s)', assignment, user, user_path)
            if not options.simulate:
                func(assignment, user, user_path, *args)


# XXX to be removed
def show(assignment, user, location):
    """Demo function"""
    print 'A:', assignment, 'U:', user, 'P:', location


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parse_arguments()
    walk(show)


