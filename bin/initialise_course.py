#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-
"""Initialises the directory path for one course"""

__author__ = """Ana Savu, <ana.savu86@gmail.com>
                Lucian Adrian Grijincu <lucian.grijincu@gmail.com>"""


import os
import sqlite3
import sys
import logging
from subprocess import check_call, CalledProcessError

import misc
import vmcheckerpaths


_logger = logging.get_logger("vmchecker.initialise_course")


def _mkdir_if_not_exist(path):
    if not(os.path.isdir(path)):
        os.mkdir(path)
    else:
        _logger.info('Skipping existing directory %s' % path)


def _create_paths(paths):
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
    rel_repo_path = misc.config().get('DEFAULT', 'Repository')
    abs_repo_path = vmcheckerpaths.abspath(rel_repo_path)
    _mkdir_if_not_exist(abs_repo_path)
    
    # then, if missing, initialize a git repo in it.
    repo_path_git = os.path.join(abs_repo_path, '.git')
    if not(os.path.isdir(repo_path_git)):
        # no git repo found in the dir.
        try:
            e = os.environ
            e['GIT_DIR'] = repo_path_git
            check_call(['git', 'init'], env=e)
        except CalledProcessError:
            logging.error('cannot create git repo in %s' % repo_path_git)


def create_db_tables(db_path):
    db_conn = sqlite3.connect(db_path)
    db_cursor = db_conn.cursor()
    db_cursor.executescript("""
	CREATE TABLE studenti 
		(id INTEGER PRIMARY KEY, 
		nume TEXT);
	CREATE TABLE teme 
		(id INTEGER PRIMARY KEY,
		nume TEXT,
		deadline DATE);
	CREATE TABLE note 
		(id INTEGER PRIMARY KEY, 
		id_student INTEGER, 
		id_tema INTEGER,
		nota INTEGER,
		data TIMESTAMP default CURRENT_TIMESTAMP);
	""")
    db_cursor.close()
    db_conn.close()


def create_db():
    # check for DB existance
    db_file = vmcheckerpaths.db_file()
    if not os.path.isfile(db_file):
        create_db_tables(db_file)
    else:
        _logger.info('Skipping existing Sqlite3 DB file %s' % db_file)


def main_storer():
    create_storer_paths()
    create_storer_git_repo()
    create_db()
    _logger.info(' -- storer init done setting up paths and db file.')


def main_tester():
    create_tester_paths()
    _logger.info(' -- tester init done setting up paths and db file.')


def usage():
    print("""Usage: 
\t%s storer - initialize storer machine
\t%s tester - initialize tester machine
\t%s --help - print this message"""% (sys.argv[0], sys.argv[0], sys.argv[0]))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if (len(sys.argv) < 2):
        usage()
        exit(1)
    if cmp(sys.argv[1], 'storer') == 0:
        main_storer()
    elif cmp(sys.argv[1], 'tester') == 0:
        main_tester()
    elif cmp(sys.argv[1], '--help') == 0:
        usage()
    else:
        usage()
        exit(1)
