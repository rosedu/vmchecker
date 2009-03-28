#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Creates a homework configuration file, uploads files to repository
and sends the homework for evaluation"""

from __future__ import with_statement

__author__ = """Ana Savu <ana.savu86@gmail.com>
                Alexandru Moșoi <brtzsnr@gmail.com>"""


import ConfigParser
import os
import shutil
import sys
import time
from subprocess import check_call
from os.path import join, split, abspath, isfile, isdir, dirname
from tempfile import mkstemp
from zipfile import ZipFile

import misc
import vmcheckerpaths


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
    if os.path.isdir(location):
        shutil.rmtree(location)
    assert not os.path.exists(location)
    os.makedirs(location)

    check_call(['unzip', archive, '-d', os.path.join(location, 'archive')])

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
    _call_git(repository, 'commit', '--allow-empty', location, '-m',
            'Updated assignment `%s\' from `%s\'' % (assignment, user))

    # XXX should create a clean zip from repository
    shutil.copy(archive, join(location, 'archive.zip'))

    return assignment_config


def submit_assignment(assignment_config):
    """Submits config file for evaluation.

    This function creates a zip archive, stores it in
    $VMCHECKER_ROOT/unchecked/ directory and calls submit
    script.

    The archive contains:
        config - assignment config (eg. name, time of submission etc)
        global - global assignments config (eg. deadlines)
        archive.zip - a zip containing the homework

    """
    assignment_config = abspath(assignment_config)

    # reads user, assignment and course
    config = ConfigParser.RawConfigParser()
    with open(assignment_config) as handler:
        config.readfp(handler)

    user = config.get('Assignment', 'User')
    assignment = config.get('Assignment', 'Assignment')
    course = misc.config().get(assignment, 'Course')

    archive = join(dirname(assignment_config), './archive.zip')
    tests = misc.relative_path('tests', assignment + '.zip')

    # finds location of penalty script
    penalty = misc.relative_path(misc.config().get(assignment, 'Penalty'))
    assert isfile(penalty)

    # builds archive with configuration

    # creates the zip archive with a unique name
    fd = mkstemp(
            suffix='.zip',
            prefix='%s_%s_%s_' % (course, assignment, user),
            dir=vmcheckerpaths.dir_unchecked())
    print >>sys.stderr, 'Creating zip package at `%s\'' % fd[1]

    # adds the files to
    with os.fdopen(fd[0], 'w+b') as handler:
        zip = ZipFile(handler, 'w')
        zip.write(assignment_config, 'config')             # assignment config
        zip.write(vmcheckerpaths.config_file(), 'storer')  # storer config
        zip.write(archive, 'archive.zip')                  # assignment archive
        zip.write(tests, 'tests.zip')                      # the archive containing tests
        zip.write(penalty, 'penalty')                      # penalty script
        zip.close()


    # sends homework to tester
    submit = vmcheckerpaths.abspath(misc.config().get(assignment, 'Submit'))
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

