#! /usr/bin/python
# -*- coding: utf-8 -*-
"""Provides functionality to manipulate batches homeworks.

NOTE: It's easy to verify which assignments are valid (by
checking the sections in vmchecker_storer.ini). However,
there is no way to check which users are valid. Nevertheless,
only homeworks found in repository are submitted; invalid
arguments are silently ignored.

"""

from __future__ import with_statement

import optparse
import os
import sys
import logging

import misc


_logger = logging.getLogger('repo_walker')
cmdline = optparse.OptionParser()   # XXX how about moving these to misc
options, args = None, None


cmdline.add_option('-r', '--recursive', action='store_true', dest='recursive',
                   default=False, help='Walks everything starting from '
                                       'current working directory')
cmdline.add_option('-u', '--user', dest='user',
                   help="Specifies whose user's homeworks to walk")
cmdline.add_option('-a', '--assignment', dest='assignment',
                   help="Specifies which assignment to walk")
cmdline.add_option('-s', '--simulate', action='store_true', dest='simulate',
                   default=False, help='Does nothing. '
                                       'Only prints homeworks to walk')
cmdline.add_option('--all', action='store_true', dest='all',
                   default=False, help='Walks all submitted homeworks')


def parse_arguments():
    """Parses command-line arguments"""
    global options, args
    options, args = cmdline.parse_args()

    error = False

    if (options.user is None
            and options.assignment is None
            and options.recursive == False
            and options.all == False):
        error = True
        print ('At least one of --user, --assignment, '
               '--recursive or --all should be specified')

    if ((options.recursive or options.all)
            and (options.user is not None
                or options.assignment is not None)):
        error = True
        print ('Options --recursive and --all '
               'are incompatible with --user and --assignment')

    if options.recursive and options.all:
        error = True
        print "You can't specify both --recursive and --all"

    if error:
        cmdline.print_help(file=sys.stdout)
        exit(1)


def _simulate(assignment, user, location, func_name, args):
    """Just prints the function the function call"""
    print 'calling %s(%s, %s, %s, *%s)' % (
            func_name, repr(assignment), repr(user), repr(location), repr(args))


def _walk_assigment(assignment, assignment_path, func, args):
    """Walks all user's sources for assignment"""
    for user in os.listdir(assignment_path):
        user_path = os.path.join(assignment_path, user)

        if not os.path.isdir(user_path):
            _logger.debug('Ignoring %s (not a directory)', user_path)
            continue

        if not os.path.isfile(os.path.join(user_path, 'config')):
            _logger.debug("Ignoring %s (no `config' file)", user_path)
            continue

        if options.user is not None and options.user != user:
            _logger.debug('Ignoring %s (as requested by --user)', user_path)
            continue

        if options.recursive:
            if os.path.commonprefix((os.getcwd(), user_path)) != os.getcwd():
                _logger.debug('Ignoring %s (in current directory)',
                              user_path)
                continue

        _logger.info('Walking on %s, %s (%s)', assignment, user, user_path)
        if options.simulate:
            _simulate(assignment, user, user_path, func.func_name, args)
        else:
            func(assignment, user, user_path, *args)


def walk(func, args=()):
    """Walks the repository and calls `func' for the homeworks found.

    @param func function to be called
    @param args extra arguments to be passed
    
    For each homework call func:
        func(assigment, user, location, *args)

    """
    repo = misc.repository()

    for assignment in os.listdir(repo):
        assignment_path = os.path.join(repo, assignment)

        if not os.path.isdir(assignment_path):
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

        _walk_assigment(assignment, assignment_path, func, args)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parse_arguments()
    walk(_simulate, ('nothing', ()))


