#!/usr/bin/env python

"""A single file that holds all vmchecker relative-path info"""


import os

class VmcheckerPaths:
    """A class that encompases all the paths inside a vmchecker
    instalation"""

    def __init__(self, root):
        """Create a vmchecker paths object.
           Accepts only one argument
                - 'root'   - specify the path to the root directory
        """
        self.root = _normalize_path(root)

    def abspath(self, *segments):
        """Joins the path segments of path with VMChecker's root path"""
        return os.path.normpath(os.path.join(self.root, *segments))


    def tester_paths(self):
        """A list of all the paths relevant to the tester machine."""
        return [self.dir_queue(), self.dir_tester_unzip_tmp()]


    def storer_paths(self):
        """A list of all the paths relevant to the storer machine."""
        return [self.dir_unchecked(), self.dir_checked(),
                self.dir_backup(), self.dir_tests()]


    def root_path(self):
        """Return the path to the course root"""
        return self.root


    def dir_repository(self):
        """The absolute path of the submission dir_repository.

        This path is valid on the storer machine."""
        return self.abspath('repo')


    def dir_unchecked(self):
        """The absolute path of the unchecked homeworks.

        This path is valid on the storer machine."""
        return self.abspath('unchecked')


    def dir_checked(self):
        """The absolute path of the checked homeworks.

        This path is valid on the storer machine."""
        return self.abspath('checked')


    def dir_tests(self):
        """The absolute path of the test archives.

        This path is valid on the storer machine."""
        return self.abspath('tests')


    def dir_queue(self):
        """The absolute path of the task queue directory.
        This path is valid on the tester machine."""
        return self.abspath('queue')


    def dir_tester_unzip_tmp(self):
        """The absolute path of the directory where submission
        archives are unzipped.
        This path is valid on the tester machine."""
        return self.abspath('tmpunzip')


    def dir_backup(self):
        """The absolute path of the directory where backups
        of tasks are kept.
        This path is valid on the storer machine."""
        return self.abspath('back')


    def db_file(self):
        """The absolute path of the database file """
        return self.abspath('vmchecker.db')


    def auth_file(self):
        """An authentication file for students not in LDAP"""
        return self.abspath('auth_file.json')


    def dir_bin(self):
        """Returns absolute path for the bin/ directory"""
        return self.abspath('bin')


    def dir_assignment(self, assignment):
        """Returns path to all assignment submissions"""
        return os.path.join(self.dir_repository(), assignment)


    def dir_submission_root(self, assignment, user):
        """Returns path to latest user's submission for the given assignment"""
        return os.path.join(self.dir_repository(), assignment, user)



def dir_submission_expanded_archive(submission_root):
    """Returns the path to the users's expanded (unzipped) submission archive"""
    return os.path.join(submission_root, 'archive')


def dir_submission_results(submission_root):
    """Returns the path to the users's result for his submission of
    the given assignment"""
    return os.path.join(submission_root, 'results')


def submission_results_grade(submission_root):
    """Returns the path to the users's grade file for the given
    assignment"""
    return os.path.join(dir_submission_results(submission_root), 'grade.vmr')


def submission_archive_file(submission_root):
    """Returns the path to the users's unmodified submission
    archive"""
    return os.path.join(submission_root, 'archive.zip')


def submission_config_file(submission_root):
    """Returns the path to the users's submission configuration file

    Among others this file contains data about user, assignment,
    upload time.
    """
    return os.path.join(submission_root, 'submission-config')



def _normalize_path(path):
    """Runs a series of sanity expansions on the given path"""
    path = os.path.expanduser(path)
    assert os.path.isabs(path)
    path = os.path.normpath(path)
    return path


def _simple_test():
    """A simple test of each function defined in this file."""

    root_path = '/cucu'
    assignment = 'assignment-xxx'
    user = 'some-random-user'
    vmpaths = VmcheckerPaths(root_path)
    sbroot = vmpaths.dir_submission_root(assignment, user)
    results =  { "tester_paths   :" : vmpaths.tester_paths(),
                 "storer_paths   :" : vmpaths.storer_paths(),
                 "root_path      :" : vmpaths.root_path(),
                 "dir_repository :" : vmpaths.dir_repository(),
                 "dir_unchecked  :" : vmpaths.dir_unchecked(),
                 "dir_checked    :" : vmpaths.dir_checked(),
                 "dir_tests      :" : vmpaths.dir_tests(),
                 "dir_queue      :" : vmpaths.dir_queue(),
                 "dir_tester_unzip_tmp:" : vmpaths.dir_tester_unzip_tmp(),
                 "dir_backup     :" : vmpaths.dir_backup(),
                 "db_file        :" : vmpaths.db_file(),
                 "dir_bin        :" : vmpaths.dir_bin(),
                 "dir_assignment :" : vmpaths.dir_assignment(assignment),
                 "dir_submission_root     :" : sbroot,
                 "dir_submission_expanded_archive :" :
                     dir_submission_expanded_archive(sbroot),
                 "dir_submission_results  :" : dir_submission_results(sbroot),
                 "submission_archive_file :" : submission_archive_file(sbroot),
                 "submission_config_file  :" : submission_config_file(sbroot),
                 }
    for result in results:
        print result, results[result]
    assert vmpaths.root_path() == root_path


if __name__ == "__main__":
    _simple_test()
