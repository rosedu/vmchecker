#! /usr/bin/python
# Initialises the directory path for one course 

__author__ = 'Ana Savu, ana.savu86@gmail.com'


import os
import sqlite3
import misc

def create_db(db_path):
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

def main():
    
    base_path = misc.vmchecker_root()

    dirnames = ['unchecked', 'back', 'checked', 'tests'];
    for dirname in dirnames:
        fullpath = os.path.join(base_path, dirname)
        if not(os.path.isdir(fullpath)):
            os.mkdir(fullpath)
        else:
            print "Dir [", fullpath, "] already exists; skipping"
        
    # check for DB existance 
    if None == misc.db_file():
        create_db(os.path.join(base_path, misc.VMCHECKER_DB))
    else:
        print "DB [", misc.db_file(), "] already created; skipping"

if __name__ == '__main__':
    main()
