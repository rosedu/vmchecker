#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides functionality to manipulate batches homeworks.

NOTE: It's easy to verify which assignments are valid (by
checking the sections in vmchecker_storer.ini). However,
there is no way to check which users are valid. Nevertheless,
only homeworks found in repository are submitted; invalid
arguments are silently ignored.

"""

from __future__ import with_statement

import os
import optparse

from . import paths
from . import vmlogging

_logger = vmlogging.create_module_logger('repo_walker')



def simulate(assignment, user, location, func_name, args):
    """Just prints the function the function call"""
    print 'calling %s(%s, %s, %s, *%s)' % (
        func_name, repr(assignment), repr(user), repr(location), repr(args))



class RepoWalker:
    """Walks through all submissions in a repository and applies a
    user supplied function"""

    def __init__(self, vmcfg):
        """Create a repo walker for the course with the config file at vmcfg"""
        self.vmcfg = vmcfg
        self.vmpaths = paths.VmcheckerPaths(vmcfg.root_path())


    def walk_submission(self, assignment, user, func=simulate, args=()):
        """Runs @func on the user's submission for the given assignment"""
        path = self.vmpaths.dir_submission_root(assignment, user)
        if not os.path.exists(path):
            return
        try:
            func(assignment, user, path, *args)
        except:
            _logger.exception('%s failed for %s, %s (%s)',
                              func, assignment, user, path)


    def walk_user(self, user, func=simulate, args=()):
        """Runs @func on the user's latest submissions for all assignments"""
        for assignment in os.listdir(self.vmpaths.dir_repository()):
            self.walk_submission(assignment, user, func, args)


    def walk_assignment(self, assignment, func=simulate, args=()):
        """Runs @func on the latest submissions of @assignment from
        all users that sent that assignment"""
        for user in self.vmpaths.dir_assignment(assignment):
            self.walk_submission(assignment, user, func, args)

    def walk_all(self, func=simulate, args=()):
        """Runs @func on all submissions"""
        for assignment in os.listdir(self.vmpaths.dir_repository()):
            self.walk_assignment(assignment, func, args)

    def _walk_assignment(self, assignment, options, func, args):
        """Walks all user's sources for assignment"""

        for user in os.listdir(self.vmpaths.dir_assignment(assignment)):
            path = self.vmpaths.dir_submission_root(assignment, user)

            if not os.path.isdir(path):
                _logger.debug('Ignoring %s (not a directory)', path)
                continue

            if not os.path.isfile(paths.submission_config_file(path)):
                _logger.debug("Ignoring %s (no config file)", path)
                continue

            if options.user is not None and options.user != user:
                _logger.debug('Ignoring %s (as requested by --user)', path)
                continue

            if options.recursive:
                if os.path.commonprefix((os.getcwd(), path)) != os.getcwd():
                    _logger.debug('Ignoring %s (in current directory)', path)
                    continue

            _logger.info('Walking on %s, %s (%s)', assignment, user, path)
            try:
                func(assignment, user, path, *args)
            except:
                _logger.exception('%s failed for %s, %s (%s)',
                                  func.func_name, assignment, user, path)
                if not options.ignore_errors:
                    raise


    def _walk_repository(self, repository, options, func, args):
        """Walks the repository."""

        for assignment in os.listdir(repository):
            path = self.vmpaths.dir_assignment(assignment)

            if not os.path.isdir(path):
                _logger.debug('Ignoring %s (not a directory)', path)
                continue

            if assignment not in self.vmcfg.assignments():
                _logger.debug('Ignoring %s (not an assignment)', path)
                continue

            if options.assignment and options.assignment != assignment:
                _logger.debug('Ignoring %s (as requested by --assignment)',
                              path)
                continue

            self._walk_assignment(assignment, options, func, args)


    def walk(self, options, func, args=()):
        """Walks the repository and calls `func' for each homework found.

        @param func function to be called
        @param args extra arguments to be passed

        For each homework call func:
            func(assignment, user, location, *args)
        The behavior is controlled through command line arguments (see
        below for possible options)

        XXX Maybe having a function independent of cmdline arguments
        would be better. Maybe later.

        """
        if options.simulate:
            func = simulate
        self._walk_repository(self.vmcfg.repository_path(), options, func, args)


def check_arguments(cmdline, options):
    """Checks that arguments don't conflict"""

    if options.course_id == None:
        cmdline.error("--course_id is mandatory.")

    if (options.user is None
        and options.assignment is None
        and options.recursive == False
        and options.all == False):
        cmdline.error('At least one of --user, --assignment, '
                             '--recursive or --all should be specified')

    if ((options.recursive or options.all)
        and (options.user or options.assignment)):
        cmdline.error('Options --recursive and --all are '
                             'incompatible with --user and --assignment')

    if options.recursive and options.all:
        cmdline.error("You can't specify both --recursive and --all")


def add_optparse_group(cmdline):
    """Add a option group to @cmdline to receive parameters related to
    repo walking"""
    group = optparse.OptionGroup(cmdline, 'repo_walker.py')
    group.add_option('-c', '--course_id', help='The ID of the course for'
                       'which you resubmit the homework.')
    group.add_option('-u', '--user', dest='user',
                     help="Specifies whose user's homeworks to walk")
    group.add_option('-a', '--assignment', dest='assignment',
                     help="Specifies which assignment to walk")
    group.add_option('-r', '--recursive', action='store_true', dest='recursive',
                     default=False, help='Walks everything starting from '
                     'current working directory')
    group.add_option('--simulate', action='store_true', dest='simulate',
                     default=False, help='Only prints homeworks to walk')
    group.add_option('--all', action='store_true', dest='all',
                     default=False, help='Walks all submitted homeworks')
    group.add_option('--ignore-errors', action='store_true',
                     dest='ignore_errors', default=False, help='Ignore errors')
    cmdline.add_option_group(group)
