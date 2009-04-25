# -*- coding: utf-8 -*-
"""All paths related to vmchecker."""


import os


_STORER_CONFIG_FILE = 'vmchecker_storer.ini'
_TESTER_CONFIG_FILE = 'vmchecker_tester.ini'
GRADE_FILENAME = 'results/job_results'

root = None
repository = None

def set_root(root_):
    """Sets vmchecker root path"""
    global root

    root = os.path.expanduser(root_)
    assert os.path.isabs(root)
    root = os.path.normpath(root)


def set_repository(repository_):
    """Sets the repository path"""
    global repository

    repository = os.path.expanduser(repository_)
    repository = os.path.join(root, repository)
    repository = os.path.normpath(repository)


def abspath(*segments):
    """Joins the path segments of path with VMChecker's root path"""
    assert root!=None, """vmcheckerpaths.root is not initialized
call config.config_storer() or config.config_tester() first!"""
    return os.path.normpath(os.path.join(root, *segments))


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


def dir_bin():
    """Returns absolute path for the bin/ directory"""
    return abspath('bin')


def dir_assignment(assignment):
    """Returns path to all assignment submissions"""
    return os.path.join(repository, assignment)


def dir_user(assignment, user):
    """Returns path to last user's assignment submission"""
    return os.path.join(repository, assignment, user)
