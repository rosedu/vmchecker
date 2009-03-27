#! /usr/bin/env python2.5
# Initialises the directory path for one course 

__author__ = """ Ana Savu, <ana.savu86@gmail.com>
             Lucian Adrian Grijincu <lucian.grijincu@gmail.com>"""


import os
import sqlite3
import misc
import sys


def create_storer_paths():
    """ Create all paths used by vmchecker on the storer machine""" 
    storer_paths = misc.VmcheckerPaths().storer_paths()
    for path in storer_paths:
        if not(os.path.isdir(path)):
            os.mkdir(path)
        else:
            print("[%s] Skipping existing directory %s" % (
                sys.argv[0], path))



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
    db_file = misc.VmcheckerPaths().db_file()
    if None == db_file:
        create_db(db_file)
    else:
        print("[%s] Skipping existing Sqlite3 DB file %s" % (
            sys.argv[0], db_file))

        


def main():
    create_storer_paths()
    create_db()
    print("[%s] storer init done setting up paths and db file." % (
            sys.argv[0]))

if __name__ == '__main__':
    main()
