# -*- coding: utf-8 -*-
"""All paths related to vmchecker."""


__author__ = 'Lucian Adrian Grijincu <lucian.grijincu@gmail.com>'


import os


VMCHECKER_INI = 'vmchecker_storer.ini'


def abspath(*relative):
    return os.path.normpath(os.path.join(root(), *relative))


def root():
    assert 'VMCHECKER_ROOT' in os.environ, (
            'VMCHECKER_ROOT environment variable not defined')
    return os.path.abspath(os.environ['VMCHECKER_ROOT'])


def tester_paths():
    """A list of all the paths relevant to the tester machine."""
    return [dir_queue(), dir_tester_unzip_tmp()]


def storer_paths():
    """A list of all the paths relevant to the storer machine."""
    return [dir_unchecked(), dir_checked(),
            dir_backup(), dir_tests()]


def dir_unchecked():
    """The absolute path of the unchecked homeworks.

    This path is valid on the storer machine."""
    return abspath('unchecked')


def dir_checked():
    """The absolute path of the checked homeworks.

    This path is valid on the storer machine."""
    return abspath('checked')


def dir_tests():
    """The absolute path of the test archives.

    This path is valid on the storer machine."""
    return abspath('tests')


def dir_queue():
    """The absolute path of the task queue directory.
    This path is valid on the tester machine."""
    return abspath('queue')

def dir_tester_unzip_tmp():
    """The absolute path of the directory where submission
    archives are unzipped.
    This path is valid on the tester machine."""
    return abspath('tmpunzip')

def dir_backup():
    """The absolute path of the directory where backups
    of tasks are kept.
    This path is valid on the storer machine."""
    return abspath('back')


def db_file():
    """The absolute path of the database file """
    return abspath('vmchecker.db')


def config_file():
    """Returns absolute path for config file 'VMCHECKER_INI'"""
    path = abspath(VMCHECKER_INI)
    assert os.path.isfile(path), '%s (%s) is not a file' % (
        VMCHECKER_INI, path)
    return path


def tester_config_file():
    path = abspath('vmchecker_tester.ini')
    assert os.path.isfile(path), '%s (%s) is not a file' % (
            'vmchecker_tester.ini', path)
    return path

