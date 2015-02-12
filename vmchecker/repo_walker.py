#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides functionality to manipulate batches homeworks."""

import os
import optparse

from . import paths


def simulator_func(assignment, account, submission_root, args):
    """Just prints the function the function call"""
    print 'calling %s(%s, %s, %s, *%s)' % (
        repr(assignment), repr(account), repr(submission_root), repr(args))



class RepoWalker:
    """Walks through all submissions in a repository and applies a
    user supplied function"""

    def __init__(self, vmcfg, simulate=False):
        """Create a repo walker for the course with the config file at vmcfg"""
        self.simulate = simulate
        self.vmcfg = vmcfg
        self.vmpaths = paths.VmcheckerPaths(vmcfg.root_path())


    def walk_submission(self, assignment, account, func=simulator_func, args=()):
        """Runs @func on the account's submission for the given assignment"""
        path = self.vmpaths.dir_cur_submission_root(assignment, account)
        if not os.path.exists(path):
            return
        if self.simulate:
            func = simulator_func
        func(assignment, account, path, *args)


    def walk_account(self, account, func=simulator_func, args=()):
        """Runs @func on the account's latest submissions for all assignments"""
        for assignment in os.listdir(self.vmpaths.dir_repository()):
            self.walk_submission(assignment, account, func, args)


    def walk_assignment(self, assignment, func=simulator_func, args=()):
        """Runs @func on the latest submissions of @assignment from
        all accounts that sent that assignment"""

        dir_assignment = self.vmpaths.dir_assignment(assignment)
        if not os.path.exists(dir_assignment):
            # if no student sent a submission for this assignment, there's noting to do
            return
        for account in os.listdir(dir_assignment):
            # skip over files that may be in the assignment directory (e.g. a '.lock' file)
            if not os.path.isdir(os.path.join(dir_assignment, account)):
                continue
            self.walk_submission(assignment, account, func, args)


    def walk_all(self, func=simulator_func, args=()):
        """Runs @func on all submissions"""
        for assignment in self.vmcfg.assignments():
            self.walk_assignment(assignment, func, args)


    def walk(self, account=None, assignment=None, func=simulator_func, args=()):
        """Walk submissions based on the combination of arguments:

        @account and @assignment can be used to narrow the search:

          * account==None, assignment==None -- compute all grades
          * account==None, assignment!=None -- all submissions for the assignment
          * account!=None, assignment==None -- all submissions from the account
          * account!=None, assignment!=None -- the account's last submission for the assignment
          """

        if account == None and assignment == None:
            self.walk_all(func, args)
        elif account != None and assignment != None:
            self.walk_submission(assignment, account, func, args)
        elif assignment != None:
            self.walk_assignment(assignment, func, args)
        elif account != None:
            self.walk_account(account, func, args)



def check_arguments(cmdline, options):
    """Checks that arguments don't conflict"""

    if options.course_id == None:
        cmdline.error("--course_id is mandatory.")

    if (options.account is None
        and options.assignment is None
        and options.all == False):
        cmdline.error('At least one of --account, --assignment'
                      ' or --all should be specified.')

    if (options.all and (options.account or options.assignment)):
        cmdline.error('Option --all is incompatible with --account and --assignment')



def add_optparse_group(cmdline):
    """Add a option group to @cmdline to receive parameters related to
    repo walking"""
    group = optparse.OptionGroup(cmdline, 'repo_walker.py')
    group.add_option('-c', '--course_id', help='The ID of the course')
    group.add_option('-u', '--account', dest='account', default=None,
                     help="Specifies which account's submissions to walk")
    group.add_option('-a', '--assignment', dest='assignment', default=None,
                     help="Specifies which assignment to walk")
    group.add_option('--simulate', action='store_true', dest='simulate',
                     default=False, help='Only prints homeworks to walk')
    group.add_option('--all', action='store_true', dest='all',
                     default=False, help='Walks all submitted homeworks')
    cmdline.add_option_group(group)
