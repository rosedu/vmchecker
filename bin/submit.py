#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Creates a homework configuration file, uploads files to repository
and sends the homework for evaluation

For a better submission scheme see the commit:
    22326889e780121f37598532efc1139e21daab41

"""

from __future__ import with_statement

__author__ = """Ana Savu <ana.savu86@gmail.com>
                Alexandru Moșoi <brtzsnr@gmail.com>"""


import ConfigParser
import errno
import fcntl
import logging
import tempfile
import os
import shutil
import sys
import time
import getpass
import subprocess
import zipfile

import config
import vmcheckerpaths


_logger = logging.getLogger('vmchecker.submit')


def _call_git(repository, *args):
    return subprocess.check_call(['git',
        '--git-dir=' + os.path.join(repository, '.git'),
        '--work-tree=' + repository] + list(args))


class _Locker(object):
    def __init__(self, assignment):
        self.__fd = os.open(
                os.path.join(vmcheckerpaths.repository, assignment, '.lock'),
                os.O_CREAT | os.O_RDWR, 0600)
        assert self.__fd != -1

    def __enter__(self):
        fcntl.lockf(self.__fd, fcntl.LOCK_EX)

    def __exit__(self, type, value, traceback):
        fcntl.lockf(self.__fd, fcntl.LOCK_UN)

    def __del__(self):
        os.close(self.__fd)


def _build_temporary_config(assignment, user, archive):
    # the upload time is the system's current time
    upload_time = time.strftime(config.DATE_FORMAT)

    location = tempfile.mkdtemp(
            prefix='%s_%s_%s_%s_' % (
                config.assignments.course(assignment),
                assignment, user, upload_time),
            dir=vmcheckerpaths.dir_backup())

    # unzips sources files
    subprocess.check_call(['unzip', archive, '-d',
                os.path.join(location, 'archive')])

    # creats homework's configuration file
    # hrc = homework resource configuration
    hrc = ConfigParser.RawConfigParser()
    hrc.add_section('Homework')
    hrc.set('Homework', 'User', user)
    hrc.set('Homework', 'Assignment', assignment)
    hrc.set('Homework', 'UploadTime', upload_time)

    # XXX these should go to `callback'
    hrc.set('Homework', 'ResultsDest',
                          os.path.join(location, 'results'))
    hrc.set('Homework', 'RemoteUsername', getpass.getuser())
    hrc.set('Homework', 'RemoteHostname', 'cs.pub.ro')

    with open(os.path.join(location, 'config'), 'w') as handler:
        hrc.write(handler)

    _logger.info('Stored homework at temporary directory %s', location)
    return location


def save_homework(assignment, user, location):
    """Saves user's submition of assignment stored at location."""
    # copies location to a temporary directory
    temp = tempfile.mkdtemp()
    src = os.path.join(temp, user)
    shutil.copytree(location, src)

    with _Locker(assignment):
        dest = os.path.join(vmcheckerpaths.repository, assignment, user)
        _logger.info("Storing user's files at %s", dest)

        # removes old files
        try:
            shutil.rmtree(dest)
            _logger.info('Removed old directory %s', dest)
        except OSError, exc:
            if exc.errno != errno.ENOENT:
                raise
            _logger.info('Ignored missing directory %s', dest)

        # brings new files
        _logger.debug('moving\nfrom %s\n  to %s', src, dest)
        shutil.move(src, dest)
        _logger.info('files stored')

        # and commits them
        repository = vmcheckerpaths.repository
        cwd = os.getcwd()
        os.chdir(dest)

        subprocess.check_call(('git', 'add', '--all', '.'))
        subprocess.check_call(('git', 'commit', '--allow-empty', '.',
                '-m', "Updated %s's submition for %s." % (user, assignment)))

        os.chdir(cwd)

    shutil.rmtree(temp)
    return dest


def build_config(assignment, user, archive):
    """Builds a configuration file for user's assignment submition.

    Returns the absolute path of the homework

    """
    assert assignment in config.assignments, (
        'No such assignment `%s\'.' % assignment)

    location = save_homework(
            assignment, user,
            _build_temporary_config(assignment, user, archive))

    # copies the zip archive
    # XXX should create a clean zip from repository
    shutil.copy(archive, os.path.join(location, 'archive.zip'))

    return location


def submit_homework(location):
    """Submits homework at location for evaluation

    This function creates a zip archive in the ./unchecked/
    directory and calls the submit script.

    The archive contains:
        config - assignment config (eg. name, time of submission etc)
        archive.zip - a zip containing the homework
        tests.zip - a zip containing the tests
        callback - a script executed by the tester to send results back
        ... - assignment's extra files (see assigments.Assignments.include())

    """
    # reads user, assignment and course
    hrc = ConfigParser.RawConfigParser()
    with open(os.path.join(location, 'config')) as handler:
        hrc.readfp(handler)

    user = hrc.get('Homework', 'User')
    assignment = hrc.get('Homework', 'Assignment')
    course = config.assignments.course(assignment)

    # location of student's homework
    # XXX should create a clean zip from the repository
    archive = os.path.join(location, 'archive.zip')
    assert os.path.isfile(archive), 'Missing archive %s' % archive

    # location of tests
    tests = config.assignments.tests(assignment)
    assert os.path.isfile(tests), 'Missing tests %s' % tests

    # builds archive with configuration
    with _Locker(assignment):
        # creates the zip archive with an unique name
        fd = tempfile.mkstemp(
                suffix='.zip',
                prefix='%s_%s_%s_' % (course, assignment, user),
                dir=vmcheckerpaths.dir_unchecked())
        _logger.info('Creating zip package %s', fd[1])

        # populates the archive (see the function's docstring)
        try:
            with os.fdopen(fd[0], 'w+b') as handler:
                zip_ = zipfile.ZipFile(handler, 'w')
                zip_.write(os.path.join(location, 'config'), 'config')
                zip_.write(archive, 'archive.zip')
                zip_.write(tests, 'tests.zip')

                # includes extra required files
                for dest, src in config.assignments.include(assignment):
                    src = vmcheckerpaths.abspath(src)

                    # XXX do not assert, but raise
                    assert os.path.isfile(src), 'File %s is missing' % src

                    zip_.write(src, dest)
                    _logger.info('Included %s as %s', src, dest)

                zip_.close()
        except:
            _logger.error('Failed to create zip archive %s', fd[1])
            os.unlink(fd[1])
            raise

    # package created, sends homework to tester by invoking submition script
    submit = config.assignments.get(assignment, 'submit')
    submit = vmcheckerpaths.abspath(submit)
    _logger.info('Invoking submission script %s', submit)
    try:
        subprocess.check_call((submit, fd[1]))
    except:
        _logger.fatal('Cannot submit homework. Archive %s not deleted.', fd[1])
        raise


def print_help():
    """Prints help and exits

    XXX change to use optparse

    """
    print >> sys.stderr, 'Usage:'
    print >> sys.stderr, '\t%s assignmen user archive' % sys.argv[0]
    print >> sys.stderr, '\t\tbuilds configuration and submits the '\
                         'assignment for evaluation'
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
        location = build_config(user, assignment, archive)
    else:
        print_help()
        exit(1)

    print >> sys.stderr, 'Homework located at %s' % location
    submit_homework(location)


if __name__ == '__main__':
    config.config_storer()
    logging.basicConfig(level=logging.DEBUG)
    main()

