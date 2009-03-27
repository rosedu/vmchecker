#! /usr/bin/env python2.5
# Initialises the directory path for one course 

__author__ = """ Ana Savu, <ana.savu86@gmail.com>
             Lucian Adrian Grijincu <lucian.grijincu@gmail.com>"""


import os
import sqlite3
import misc
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("vmchecker.initialise_course")


def _mkdir_if_not_exist(path):
    if not(os.path.isdir(path)):
        os.mkdir(path)
    else:
        logger.info("Skipping existing directory %s" % path)

def _create_paths(paths):
    for path in paths:
        _mkdir_if_not_exist(path)

def create_tester_paths():
    """ Create all paths used by vmchecker on the storer machine""" 
    tester_paths = misc.vmcheckerPaths.tester_paths
    _create_paths(tester_paths)


def create_storer_paths():
    """ Create all paths used by vmchecker on the storer machine""" 
    storer_paths = misc.vmcheckerPaths.storer_paths
    _create_paths(storer_paths)


def create_storer_git_repo():
    """ Create the repo for the assignments on the storer """
    repo_path = misc.config().get("DEFAULT", "Repository")
    _mkdir_if_not_exist(repo_path)

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
    db_file = misc.vmcheckerPaths.db_file
    if None == db_file:
        create_db(db_file)
    else:
        logger.info("Skipping existing Sqlite3 DB file %s" % db_file)

        


def main_storer():
    create_storer_paths()
    create_storer_git_repo()
    create_db()
    logger.info(" -- storer init done setting up paths and db file.")

def main_tester():
    create_tester_paths()
    logger.info(" -- tester init done setting up paths and db file.")

def usage():
    print("""Usage: 
\t%s storer - initialize storer machine
\t%s tester - initialize tester machine
\t%s --help - print this message""" % (sys.argv[0], sys.argv[0], sys.argv[0]))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        usage()
        exit(1)
    if   cmp(sys.argv[1], "storer") == 0:
        main_storer()
    elif cmp(sys.argv[1], "tester") == 0:
        main_tester()
    elif cmp(sys.argv[1], "--help") == 0:
        usage()
    else:
        usage()
        exit(1)
