#!/usr/bin/env python

"""A single file that holds all vmchecker relative-path info"""


import os

class VmcheckerPaths:
    def __init__(self, root):
        """Create a vmchecker paths object.
           Accepts only one argument
                - 'root'   - specify the path to the root directory        
        """
        self.root = root

    def _normalize_root(self, path):
        """Sets vmchecker root path"""
        path = os.path.expanduser(path)
        assert os.path.isabs(path)
        path = os.path.normpath(path)
        return path


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


    def dir_bin(self):
        """Returns absolute path for the bin/ directory"""
        return self.abspath('bin')


    def dir_assignment(self, assignment):
        """Returns path to all assignment submissions"""
        return os.path.join(self.dir_repository(), assignment)


    def dir_user(self, assignment, user):
        """Returns path to last user's assignment submission"""
        return os.path.join(self.dir_repository(), assignment, user)


    def dir_results(self, assignment, user):
        """Returns path to user's results on assignment"""
        return os.path.join(self.dir_repository(), assignment, user, 'results')

if __name__ == "__main__":
    v = VmcheckerPaths(root = '/cucu')
    result =  { "tester_paths   :" : v.tester_paths(),
            "storer_paths   :" : v.storer_paths(),
            "dir_repository :" : v.dir_repository(),
            "dir_unchecked  :" : v.dir_unchecked(),
            "dir_checked    :" : v.dir_checked(),
            "dir_tests      :" : v.dir_tests(),
            "dir_queue      :" : v.dir_queue(),
            "dir_tester_unzip_tmp:" : v.dir_tester_unzip_tmp(),
            "dir_backup     :" : v.dir_backup(),
            "db_file        :" : v.db_file(),
            "dir_bin        :" : v.dir_bin(),
            "dir_assignment :" : v.dir_assignment('aaa'),
            "dir_usee       :" : v.dir_user('aaa', 'uuu'),
            "dir_results    :" : v.dir_results('aaa', 'uuu'),
    }
    for r in result:
        print r, result[r]


