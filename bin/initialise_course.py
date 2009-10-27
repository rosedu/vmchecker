#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialises the directory path for one course"""

from __future__ import with_statement

import os
import sqlite3
import sys
import logging
import string
from subprocess import check_call, CalledProcessError

import vmcheckerpaths
import config


_logger = logging.getLogger("vmchecker.initialise_course")


def _install_example_config_file():
    """Install an example config file to ~/.vmcheckerrc"""

    # get the data from the example .vmcheckerrc
    template_data = ""
    with open('examples/.vmcheckerrc') as template:
        template_data = template.read()

    # the example is a template that contains some '$var' variables.
    s = string.Template(template_data)

    # first, determine some sane values for those variables
    default_root = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    default_repo = os.path.normpath(os.path.join(default_root, '..', 'repo'))

    # replace the $vars with these values and write the result in the destination file
    with open(config.vmcheckerrc_path(), 'w') as handle:
        handle.write(s.substitute(root=default_root, repo=default_repo))


def _install_if_needed_example_config_file():
    if not os.path.exists(config.vmcheckerrc_path()):
        _install_example_config_file()
        print(('A new default vmchecker configuration file was written to %s. ' +
               'Please update it before running any vmchecker code.') % config.vmcheckerrc_path())
    else:
        print(('Configuration file %s exists. This script will not change it.') %  config.vmcheckerrc_path())

def _mkdir_if_not_exist(path):
    """Make the path if it does not exist"""
    if not(os.path.isdir(path)):
        os.mkdir(path)
    else:
        _logger.info('Skipping existing directory %s' % path)


def _create_paths(paths):
    """ Create all paths in the received 'paths' parameter"""
    for path in paths:
        _mkdir_if_not_exist(path)


def create_tester_paths():
    """Create all paths used by vmchecker on the storer machine"""
    _create_paths(vmcheckerpaths.tester_paths())


def create_storer_paths():
    """Create all paths used by vmchecker on the storer machine"""
    _create_paths(vmcheckerpaths.storer_paths())


def create_storer_git_repo():
    """Creates the repo for the assignments on the storer."""
    # first make teh destination directory
    rel_repo_path = vmcheckerpaths.repository
    abs_repo_path = vmcheckerpaths.abspath(rel_repo_path)
    _mkdir_if_not_exist(abs_repo_path)

    # then, if missing, initialize a git repo in it.
    repo_path_git = os.path.join(abs_repo_path, '.git')
    if not(os.path.isdir(repo_path_git)):
        # no git repo found in the dir.
        try:
            env = os.environ
            env['GIT_DIR'] = repo_path_git
            check_call(['git', 'init'], env=env)
        except CalledProcessError:
            logging.error('cannot create git repo in %s' % repo_path_git)


def create_db_tables(db_path):
    """Create a sqlite db file în db_path for grade management."""
    db_conn = sqlite3.connect(db_path)
    db_cursor = db_conn.cursor()
    db_cursor.executescript("""
    CREATE TABLE assignments (
        id INTEGER PRIMARY KEY,
        name TEXT);
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT);
    CREATE TABLE grades (
        assignment_id INTEGER,
        user_id INTEGER,
        grade TEXT,
        mtime TIMESTAMP NOT NULL,
        PRIMARY KEY(assignment_id, user_id));
    """)
    db_cursor.close()
    db_conn.close()


def create_db():
    """Create the implicit db if it does not exist."""
    # check for DB existance
    db_file = vmcheckerpaths.db_file()
    if not os.path.isfile(db_file):
        create_db_tables(db_file)
    else:
        _logger.info('Skipping existing Sqlite3 DB file %s' % db_file)


def main_storer():
    """Run initialization tasks for the storer machine."""
    config.config_storer()
    create_storer_paths()
    create_storer_git_repo()
    create_db()
    _logger.info(' -- storer init done setting up paths and db file.')


def main_tester():
    """Run initialization tasks for the tester machine."""
    config.config_tester()
    create_tester_paths()
    _logger.info(' -- tester init done setting up paths and db file.')


def usage():
    """Print usage for this program."""
    print("""Usage:
\t%s storer - initialize storer machine
\t%s tester - initialize tester machine
\t%s --help - print this message"""% (sys.argv[0], sys.argv[0], sys.argv[0]))


def main():
    """Initialize course based on sys.argv."""
    logging.basicConfig(level=logging.DEBUG)
    config.parse_arguments()
    if (len(sys.argv) < 2):
        usage()
        exit(1)
    if cmp(sys.argv[1], 'storer') == 0:
        _install_if_needed_example_config_file()
        main_storer()
    elif cmp(sys.argv[1], 'tester') == 0:
        _install_if_needed_example_config_file()
        main_tester()
    elif cmp(sys.argv[1], '--help') == 0:
        usage()
    else:
        usage()
        exit(1)

if __name__ == '__main__':
    main()
