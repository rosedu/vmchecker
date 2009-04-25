#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Creates a homework configuration file, uploads files to repository
and sends the homework for evaluation"""

from __future__ import with_statement

__author__ = """Ana Savu <ana.savu86@gmail.com>
                Alexandru Moșoi <brtzsnr@gmail.com>"""


import ConfigParser
import errno
import fcntl
import logging
import os
import shutil
import sys
import time
import getpass
from subprocess import check_call
from os.path import abspath, dirname
from tempfile import mkstemp
from zipfile import ZipFile

import config
import assignments
import vmcheckerpaths


_logger = logging.getLogger('vmchecker.submit')


def _call_git(repository, *args):
    return check_call(['git',
        '--git-dir=' + os.path.join(repository, '.git'),
        '--work-tree=' + repository] + list(args))


class _Locker(object):
    def __init__(self, assignment):
        self.fd = os.open(
                os.path.join(vmcheckerpaths.repository, assignment, '.lock'),
                os.O_CREAT | os.O_RDWR, 0600)
        assert self.fd != -1

    def __enter__(self):
        fcntl.lockf(self.fd, fcntl.LOCK_EX)

    def __exit__(self, type, value, traceback):
        fcntl.lockf(self.fd, fcntl.LOCK_UN)

    def __del__(self):
        os.close(self.fd)


def build_config(user, assignment, archive):
    """Builds a configuration file for user's assignment.

    Returns absolute path to assignment config.

    XXX Exit code of child processes is not checked.
    XXX Locks should protect the directory access"""
    assert assignment in assignments.assignments(), (
        'No such assignment `%s\'.' % assignment)

    # the upload time is the system's current time
    upload_time = time.strftime(config.DATE_FORMAT)

    # repository's path
    repository = vmcheckerpaths.repository

    # creates a temporary directory to store homework
    location = os.path.join(repository, assignment)
    try:
        os.makedirs(location)
        _logger.info("created `%s'", location)
    except OSError, exc:
        if exc.errno != errno.EEXIST:
            raise
        _logger.info("`%s' already exists", location)

    with _Locker(assignment):
        location = os.path.join(location, user)
        _logger.info("Storing student's files at `%s'", location)

        try:
            shutil.rmtree(location)
            _logger.info("Removed old `%s'", location)
        except OSError, exc:
            if exc.errno != errno.ENOENT:
                raise
            _logger.info("Ignoring missing `%s'", location)

        os.makedirs(location)

        # brings necessary files
        check_call(['unzip', archive, '-d',
                    os.path.join(location, 'archive')])

        # writes assignment configuration file
        assignment_config = os.path.join(location, 'config')

        with open(assignment_config, 'w') as handle:
            handle.write('[Assignment]\n')
            handle.write('User=%s\n' % user)
            handle.write('Assignment=%s\n' % assignment)
            handle.write('UploadTime=%s\n' % upload_time)
            # these should go to `callback'
            handle.write('ResultsDest=%s\n'    % os.path.join(location, 'results'))
            handle.write('RemoteUsername=%s\n' % getpass.getuser())
            handle.write('RemoteHostname=%s\n' % 'cs.pub.ro')

        _logger.info('stored homework files. overwriting old homework')

        # commits all new files from 'location' that are not ignored by .gitignore
        _call_git(repository, 'add', '--all', location)
        _call_git(repository, 'commit', '--allow-empty', location, '-m',
                "Updated `%s''s submition for `%s'." % (user, assignment))

        # XXX should create a clean zip from repository
        shutil.copy(archive, os.path.join(location, 'archive.zip'))
        return assignment_config


def submit_assignment(assignment_config):
    """Submits config file for evaluation.

    This function creates a zip archive in the ./unchecked/
    directory and calls the submit script.

    The archive contains:
        config - assignment config (eg. name, time of submission etc)
        global - global assignments config (eg. deadlines)
        archive.zip - a zip containing the homework
        callback - a script executed by the tester to send results back

    """
    assignment_config = abspath(assignment_config)

    # reads user, assignment and course
    aconfig = ConfigParser.RawConfigParser()
    with open(assignment_config) as handler:
        aconfig.readfp(handler)

    user = aconfig.get('Assignment', 'User')
    assignment = aconfig.get('Assignment', 'Assignment')
    course = assignments.get(assignment, 'Course')

    # location of student's homework
    archive = os.path.join(dirname(assignment_config), 'archive.zip')
    assert os.path.isfile(archive), "Missing archive `%s'" % archive

    # location of tests
    tests = os.path.join(vmcheckerpaths.dir_tests(), assignment + '.zip')
    assert os.path.isfile(tests), "Missing tests `%s'" % tests

    # builds archive with configuration
    with _Locker(assignment):
        # creates the zip archive with an unique name
        fd = mkstemp(
                suffix='.zip',
                prefix='%s_%s_%s_' % (course, assignment, user),
                dir=vmcheckerpaths.dir_unchecked())
        _logger.info("Creating zip package at `%s'", fd[1])

        # populates the archive
        # Includes at least these files:
        #   config -> homework config (see above)
        #   archive.zip -> homework files (student's sources)
        #   tests.zip -> assignment tests
        try:
            with os.fdopen(fd[0], 'w+b') as handler:
                zip = ZipFile(handler, 'w')
                zip.write(assignment_config, 'config')   # assignment config
                zip.write(archive, 'archive.zip')        # assignment archive
                zip.write(tests, 'tests.zip')            # the archive containing tests

                # includes extra required files
                for dst, src in assignments.include(assignment):
                    src = vmcheckerpaths.abspath(src)
                    assert os.path.isfile(src), "`%s' is missing" % src

                    zip.write(src, dst)
                    _logger.debug("Included `%s' as `%s'.", src, dst)

                zip.close()
        except:
            _logger.error("Failed to create archive `%s'", fd[1])
            os.unlink(fd[1])
            raise

        # sends homework to tester
        submit = assignments.path(assignment, 'submit')
        _logger.info('Calling submission script %s', submit)
        try:
            check_call((submit, fd[1]))
        except:
            _logger.fatal("Cannot submit homework. Archive `%s' not deleted.", fd[1])
            raise


def print_help():
    """Prints help and exits

    XXX change to use optparse

    """
    print >> sys.stderr, 'Usage:'
    print >> sys.stderr, '\t%s user assignment archive' % sys.argv[0]
    print >> sys.stderr, '\t\tbuilds config and submits assignment for evaluation'
    print >> sys.stderr, '\t%s config' % sys.argv[0]
    print >> sys.stderr, '\t\tresubmits assignment for reevaluation'


def main():
    if len(sys.argv) == 1:
        print_help()
        exit(1)
    elif len(sys.argv) == 2:
        if not os.path.isfile(sys.argv[1]):
            print >> sys.stderr, '`%s\' must be an existing file.' % sys.argv[1]
            print_help()
            exit(1)

        assignment_config = sys.argv[1]
    elif len(sys.argv) == 4:
        if not os.path.isfile(sys.argv[3]):
            print >> sys.stderr, '`%s\' must be an existing file.' % sys.argv[3]
            print_help()
            exit(1)

        user = sys.argv[1]           # student's name
        assignment = sys.argv[2]     # assignment
        archive = sys.argv[3]        # archive
        assignment_config = build_config(user, assignment, archive)
    else:
        print_help()
        exit(1)

    print >> sys.stderr, 'Assignment config located at `%s\'' % assignment_config
    submit_assignment(assignment_config)


if __name__ == '__main__':
    config.config_storer()
    logging.basicConfig(level=logging.DEBUG)
    main()

