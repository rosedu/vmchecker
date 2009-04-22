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

import vmcheckerpaths
import config


_logger = logging.getLogger('repo_walker')


def _check_arguments():
    """Checks that arguments don't conflict"""
    from config import options

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
        config.cmdline.print_help(file=sys.stdout)
        exit(1)


def _simulate(assignment, user, location, func_name, args):
    """Just prints the function the function call"""
    print 'calling %s(%s, %s, %s, *%s)' % (
            func_name, repr(assignment), repr(user), repr(location), repr(args))


def _walk_assigment(assignment, assignment_path, func, args):
    """Walks all user's sources for assignment"""
    from config import options

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


def _walk_repository(repository, func, args):
    """Walks the repository."""
    from config import options

    for assignment in os.listdir(repository):
        assignment_path = os.path.join(repository, assignment)

        if not os.path.isdir(assignment_path):
            _logger.debug('Ignoring %s (not a directory)', assignment_path)
            continue

        # XXX maybe an `assignment' module would be appropriate
        if assignment not in config.get():
            _logger.debug('Ignoring %s (not an assignment)', assignment_path)
            continue

        if options.assignment is not None and options.assignment != assignment:
            _logger.debug('Ignoring %s (as requested by --assignment)',
                          assignment_path)
            continue

        _walk_assigment(assignment, assignment_path, func, args)


def walk(func, args=()):
    """Walks the repository and calls `func' for each homework found.

    @param func function to be called
    @param args extra arguments to be passed

    For each homework call func:
        func(assigment, user, location, *args)
    The behavior is controlled through command line arguments (see
    below for possible options)

    XXX Maybe having a function independent of cmdline arguments
    would be better. Maybe later.

    """
    _check_arguments()
    _walk_repository(vmcheckerpaths.repository, func, args)


group = optparse.OptionGroup(config.cmdline, 'repo_walker.py')
group.add_option('-u', '--user', dest='user',
                 help="Specifies whose user's homeworks to walk")
group.add_option('-a', '--assignment', dest='assignment',
                 help="Specifies which assignment to walk")
group.add_option('-r', '--recursive', action='store_true', dest='recursive',
                 default=False, help='Walks everything starting from '
                                     'current working directory')
group.add_option('-s', '--simulate', action='store_true', dest='simulate',
                 default=False, help='Only prints homeworks to walk')
group.add_option('--all', action='store_true', dest='all',
                 default=False, help='Walks all submitted homeworks')
config.cmdline.add_option_group(group)
del group

