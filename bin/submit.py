#! /usr/bin/env python
# Creates a homework configuration file, uploads files to repository
# and sends the homework for evaluation

from __future__ import with_statement

__author__ = 'Ana Savu ana.savu86@gmail.com, Alexandru V. Mosoi brtzsnr@gmail.com'

import ConfigParser
import misc
import os
import shutil
import sys
import time

from subprocess import check_call
from os.path import join, split, abspath, isfile, isdir
from tempfile import mkstemp


def _call_git(repository, *args):
    return check_call(['git',
        '--git-dir=' + join(repository, '.git'),
        '--work-tree=' + repository] + list(args))


def build_config(user, assignment, archive):
    """Builds a coonfiguration file for user's assignment.

    Returns absolute path to assignment config.

    XXX Exit code of child processes is not checked.
    XXX Locks should protect the directory access"""
    assert assignment in misc.config().sections(), (
        'No such assigment `%s\'.' % assignment)
    repository = misc.repository(assignment)

    # the upload time is the system's current time
    upload_time = time.strftime(misc.DATE_FORMAT)

    location = join(repository, assignment, user)
    print >>sys.stderr, 'Storing files at `%s\'' % location

    # removes the old homework and adds the new one
    # NOTE: git is clever enough to store only diffs
    shutil.rmtree(location)
    os.makedirs(location)
    check_call(('unzip', archive, '-d', join(location, 'archive')))

    # writes assignment configuration file
    assignment_config = join(location, 'config')

    with open(assignment_config, 'w') as handle:
        handle.write('[Assignment]\n')
        handle.write('User=%s\n' % user)
        handle.write('Assignment=%s\n' % assignment)
        handle.write('UploadTime=%s\n' % upload_time)

    # commits the changes
    _call_git(repository, 'add', location)
    _call_git(repository, 'clean', location, '-f', '-d')
    _call_git(repository, 'commit', location, '-m',
            'Updated assignment `%s\' from `%s\'' % (assignment, user))

    return assignment_config


def submit_assignment(assignment_config):
    """Submits config file for evaluation."""
    assignment_config = abspath(assignment_config)

    # reads user, assignment and course
    config = ConfigParser.RawConfigParser()
    with open(assignment_config) as handler:
        config.readfp(handler)
    user = config.get('Assignment', 'User')
    assignment = config.get('Assignment', 'Assignment')
    course = misc.config().get(assignment, 'Course')

    # builds archive with configuration
    location = join(misc.vmchecker_root(), 'unchecked')
    assert isdir(location), 'No such directory `unchecked\''
    fd = mkstemp(
            suffix='.tgz',
            prefix='%s_%s_%s_' % (course, assignment, user),
            dir=location)
    print >>sys.stderr, 'Config files stored at `%s\'' % fd[1]

    _a = split(assignment_config)
    _c = split(misc.config_file())
    with os.fdopen(fd[0]) as handler:
        check_call(('tar', '-cz',
            '-C', _a[0], _a[1],         # assignment
            '-C', _c[0], _c[1],         # global config
                                        # machine information (TODO)
            ), stdout=handler)

    # sends homework to tester
    submit = misc.config().get(assignment, 'Submit')
    submit = join(misc.vmchecker_root(), submit)
    check_call((submit, fd[1]))


def print_help():
    """Prints help and exits"""
    print >>sys.stderr, 'Usage:'
    print >>sys.stderr, '\t%s user assignment archive' % sys.argv[0]
    print >>sys.stderr, '\t\tbuilds config and submits assignment for evaluation'
    print >>sys.stderr, '\t%s config' % sys.argv[0]
    print >>sys.stderr, '\t\tresubmits assignment for reevaluation'
    sys.exit(1)


def main():
    if len(sys.argv) == 1:
        print_help()

    if len(sys.argv) == 2:
        if not isfile(sys.argv[1]):
            print >>sys.stderr, '`%s\' must be an existing file.' % sys.argv[1]
            print_help()

        assignment_config = sys.argv[1]
    elif len(sys.argv) == 4:
        if not isfile(sys.argv[3]):
            print >>sys.stderr, '`%s\' must be an existing file.' % sys.argv[3]
            print_help()

        user = sys.argv[1]           # student's name
        assignment = sys.argv[2]     # assignment
        archive = sys.argv[3]        # archive
        assignment_config = build_config(user, assignment, archive)
    else:
        print_help()

    print >>sys.stderr, 'Assignment config located at `%s\'' % assignment_config
    submit_assignment(assignment_config)


if __name__ == '__main__':
    main()

