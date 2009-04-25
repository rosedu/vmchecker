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
import getpass
import logging
import os
import shutil
import subprocess
import tempfile
import time
import datetime
import optparse
import zipfile

import config
import vmcheckerpaths


_logger = logging.getLogger('submit')


def _build_temporary_config(assignment, user, archive):
    """Stores user's submission of assignment in a temporary directory"""

    # the upload time is the system's current time
    upload_time = time.strftime(config.DATE_FORMAT)
    prefix = '%s_%s_%s_%s_' % (
            config.assignments.course(assignment),
            assignment, user, upload_time)

    # first saves the zip archive
    location = tempfile.mkstemp(
            prefix=prefix,
            suffix='.zip',
            dir=vmcheckerpaths.dir_backup())
    shutil.copy(archive, location[1])
    os.close(location[0])

    # location is the temporary destination directory
    location = tempfile.mkdtemp(
            prefix=prefix,
            dir=vmcheckerpaths.dir_backup())

    # unzips sources files
    subprocess.check_call(['unzip', archive,
            '-d', os.path.join(location, 'archive')])

    # creates homework's configuration file
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
    """Saves user's submission of assignment stored at location."""
    # copies location to a temporary directory
    temp = tempfile.mkdtemp()
    src = os.path.join(temp, user)
    shutil.copytree(location, src)

    with config.assignments.lock(assignment):
        dest = vmcheckerpaths.homework_path(assignment, user)
        _logger.info("Storing user's files at %s", dest)

        # removes old files
        try:
            shutil.rmtree(dest)
            _logger.info('Removed old directory %s', dest)
        except OSError, exc:
            if exc.errno != errno.ENOENT:
                raise
            _logger.info('Ignored missing directory %s', dest)

        # brings the new files
        _logger.debug('Moving\nfrom %s\n  to %s', src, dest)
        shutil.move(src, dest)
        _logger.info('files stored')

        # and commits them
        cwd = os.getcwd()
        os.chdir(dest)

        subprocess.check_call(('git', 'add', '--all', '.'))
        subprocess.check_call(('git', 'commit', '--allow-empty', '.',
                '-m', "Updated %s's submission for %s." % (user, assignment)))

        os.chdir(cwd)

    shutil.rmtree(temp)
    return dest


def build_config(assignment, user, archive):
    """Builds a configuration file for user's assignment submission.

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
        ... - assignment's extra files (see assignments.Assignments.include())

    """
    # reads user, assignment and course
    # hrc = homework resource configuration
    hrc = ConfigParser.RawConfigParser()
    with open(os.path.join(location, 'config')) as handler:
        hrc.readfp(handler)

    assignment = hrc.get('Homework', 'Assignment')
    user = hrc.get('Homework', 'User')
    course = config.assignments.course(assignment)

    # location of student's homework
    # XXX should create a clean zip from the repository
    archive = os.path.join(location, 'archive.zip')
    assert os.path.isfile(archive), 'Missing archive %s' % archive

    # location of tests
    tests = config.assignments.tests(assignment)
    assert os.path.isfile(tests), 'Missing tests %s' % tests

    # builds archive with configuration
    with config.assignments.lock(assignment):
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

    # package created, sends homework to tester by invoking submission script
    submit = config.assignments.get(assignment, 'Submit')
    submit = vmcheckerpaths.abspath(submit)
    _logger.info('Invoking submission script %s', submit)
    try:
        subprocess.check_call((submit, fd[1]))
    except:
        _logger.fatal('Cannot submit homework %s, %s', assignment, user)
        os.unlink(fd[1])
        raise


def _get_upload_time(assignment, user):
    """Returns a datetime object with upload time user's last submission"""
    location = vmcheckerpaths.homework_path(assignment, user)
    config_file = os.path.join(location, 'config')

    if not os.path.isdir(location):
        return None
    if not os.path.isfile(config_file):
        _logger.warn('%s found, but config (%s) is missing',
                     location, config_file)
        return None

    hrc = ConfigParser.RawConfigParser()
    with open(os.path.join(location, 'config')) as handler:
        hrc.readfp(handler)

    upload_time = hrc.get('Homework', 'UploadTime')
    upload_time = time.strptime(upload_time, config.DATE_FORMAT)
    return datetime.datetime(*upload_time[:6])


def main():
    """Parse arguments and submits the homework"""

    config.cmdline.set_usage('Usage: %prog [options] assignment user archive')
    config.config_storer()

    if len(config.argv) != 3:
        config.cmdline.error('Not enough arguments')

    assignment = config.argv[0]
    user = config.argv[1]
    archive = config.argv[2]

    if not os.path.isfile(archive):
        config.cmdline.error('%s must be an existing file.' % archive)
    if assignment not in config.assignments:
        config.cmdline.error('%s must be a valid assignment.' % assignment)

    # checks time difference
    if not config.options.force:
        upload_time = _get_upload_time(assignment, user)

        if upload_time is not None:
            remaining = upload_time
            remaining += config.assignments.timedelta(assignment)
            remaining -= datetime.datetime.now()

            if remaining > datetime.timedelta():
                _logger.fatal('You are submitting too fast')
                _logger.fatal('Please allow %s between submissions',
                        str(config.assignments.timedelta(assignment)))
                _logger.fatal('Try again in %s', remaining)
                exit(1)

    location = build_config(assignment, user, archive)
    submit_homework(location)


group = optparse.OptionGroup(config.cmdline, 'submit.py')
group.add_option(
        '-f', '--force', action='store_true', dest='force', default=False,
        help='Force submitting the homework ignoring the time difference')
config.cmdline.add_option_group(group)
del group


if __name__ == '__main__':
    main()

