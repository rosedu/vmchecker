#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides functionality to manipulate batches homeworks."""

import os
import optparse

from . import paths
from . import vmlogging


def simulator_func(assignment, user, submission_root, args):
    """Just prints the function the function call"""
    print 'calling %s(%s, %s, %s, *%s)' % (
        repr(assignment), repr(user), repr(submission_root), repr(args))



class RepoWalker:
    """Walks through all submissions in a repository and applies a
    user supplied function"""

    def __init__(self, vmcfg, simulate=False):
        """Create a repo walker for the course with the config file at vmcfg"""
        self.simulate = simulate
        self.vmcfg = vmcfg
        self.vmpaths = paths.VmcheckerPaths(vmcfg.root_path())


    def walk_submission(self, assignment, user, func=simulator_func, args=()):
        """Runs @func on the user's submission for the given assignment"""
        path = self.vmpaths.dir_submission_root(assignment, user)
        if not os.path.exists(path):
            return
        try:
            if self.simulate:
                func = simulator_func
            func(assignment, user, path, *args)
        except:
            logger = vmlogging.create_module_logger('repo_walker')
            logger.exception('%s failed for %s, %s (%s)',
                             func, assignment, user, path)


    def walk_user(self, user, func=simulator_func, args=()):
        """Runs @func on the user's latest submissions for all assignments"""
        for assignment in os.listdir(self.vmpaths.dir_repository()):
            self.walk_submission(assignment, user, func, args)


    def walk_assignment(self, assignment, func=simulator_func, args=()):
        """Runs @func on the latest submissions of @assignment from
        all users that sent that assignment"""
        for user in self.vmpaths.dir_assignment(assignment):
            self.walk_submission(assignment, user, func, args)

    def walk_all(self, func=simulator_func, args=()):
        """Runs @func on all submissions"""
        for assignment in os.listdir(self.vmpaths.dir_repository()):
            self.walk_assignment(assignment, func, args)

    def walk(self, user=None, assignment=None, func=simulator_func, args=()):
        """Walk submissions based on the combination of arguments:

        @user and @assignment can be used to narrow the search:

          * user==None, assignment==None -- compute all grades
          * user==None, assignment!=None -- all submissions for the assignment
          * user!=None, assignment==None -- all submissions from the user
          * user!=None, assignment!=None -- the user's last submission for the assignment
          """

        if user == None and assignment == None:
            self.walk_all(func, args)
        elif user != None and assignment != None:
            self.walk_submission(assignment, user, func, args)
        elif assignment != None:
            self.walk_assignment(assignment, func, args)
        elif user != None:
            self.walk_user(user, func, args)



def check_arguments(cmdline, options):
    """Checks that arguments don't conflict"""

    if options.course_id == None:
        cmdline.error("--course_id is mandatory.")

    if (options.user is None
        and options.assignment is None
        and options.all == False):
        cmdline.error('At least one of --user, --assignment'
                      ' or --all should be specified.')

    if (options.all and (options.user or options.assignment)):
        cmdline.error('Option --all is incompatible with --user and --assignment')



def add_optparse_group(cmdline):
    """Add a option group to @cmdline to receive parameters related to
    repo walking"""
    group = optparse.OptionGroup(cmdline, 'repo_walker.py')
    group.add_option('-c', '--course_id', help='The ID of the course')
    group.add_option('-u', '--user', dest='user', default=None,
                     help="Specifies which user's submissions to walk")
    group.add_option('-a', '--assignment', dest='assignment', default=None,
                     help="Specifies which assignment to walk")
    group.add_option('--simulate', action='store_true', dest='simulate',
                     default=False, help='Only prints homeworks to walk')
    group.add_option('--all', action='store_true', dest='all',
                     default=False, help='Walks all submitted homeworks')
    cmdline.add_option_group(group)
