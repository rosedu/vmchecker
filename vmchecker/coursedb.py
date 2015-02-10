#!/usr/bin/env python

"""Manage the course database"""

from __future__ import with_statement

import sqlite3
from contextlib import contextmanager, closing



class CourseDb(object):
    """A class to encapsulate the logic behind updates and querries of
    the course's db"""

    def __init__(self, db_cursor):
        self.db_cursor = db_cursor

    def create_tables(self):
        """Create the tables needed for vmchecker"""
        self.db_cursor.executescript("""
             CREATE TABLE assignments (id INTEGER PRIMARY KEY, name TEXT);

             CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);

             CREATE TABLE grades (assignment_id INTEGER,
                                  user_id       INTEGER,
                                  grade         TEXT,
                                  mtime         TIMESTAMP NOT NULL,
                                  PRIMARY KEY(assignment_id, user_id));""")



    def add_assignment(self, assignment):
        """Creates an id of the homework and returns it."""
        self.db_cursor.execute('INSERT INTO assignments (name) values (?)',
                               (assignment,))
        self.db_cursor.execute('SELECT last_insert_rowid()')
        assignment_id, = self.db_cursor.fetchone()
        return assignment_id


    def get_assignment_id(self, assignment):
        """Returns the id of the assignment"""
        self.db_cursor.execute('SELECT id FROM assignments WHERE name=?',
                               (assignment,))
        result = self.db_cursor.fetchone()
        if result is None:
            return self.add_assignment(assignment)
        return result[0]


    def add_user(self, user):
        """Creates an id of the user and returns it."""
        self.db_cursor.execute('INSERT INTO users (name) values (?)', (user,))
        self.db_cursor.execute('SELECT last_insert_rowid()')
        user_id, = self.db_cursor.fetchone()
        return user_id


    def get_user_id(self, user):
        """Returns the id of the user"""
        self.db_cursor.execute('SELECT id FROM users WHERE name=?', (user,))
        result = self.db_cursor.fetchone()
        if result is None:
            return self.add_user(user)
        return result[0]


    def get_grade_mtime(self, assignment_id, user_id):
        """Returns the mtime of a grade"""
        self.db_cursor.execute('SELECT mtime FROM grades '
                               'WHERE assignment_id = ? and user_id = ?',
                               (assignment_id, user_id))
        result = self.db_cursor.fetchone()
        if result is not None:
            return result[0]


    def save_grade(self, assignment_id, user_id, grade, mtime):
        """Save the grade into the database

        If the grade identified by (assignment_id, user_id)
        exists then update the DB, else inserts a new entry.

        """
        self.db_cursor.execute('INSERT OR REPLACE INTO grades '
                               '(grade, mtime, assignment_id, user_id) '
                               'VALUES (?, ?, ?, ?) ',
                               (grade, mtime, assignment_id, user_id))

    def get_grades(self, user = None):
        """Return all the individual grades of one or all users."""
        self.db_cursor.execute('SELECT users.name, assignments.name, grades.grade ' +
                               'FROM users, assignments, student_grades ' +
                               'WHERE 1 ' +
                               'AND users.id = grades.user_id ' +
                               'AND assignments.id = grades.assignment_id ' +
                               ('AND users.name = "' + user + '"' if user != None else ''))
        return self.db_cursor.fetchall()



@contextmanager
def opening_course_db(db_file, isolation_level=None):
    """Context manager ensuring that the database resources are
    propperly closed upon either success or exception.

    On success the latest changes must be commited, while on failure
    they must be rolled back.

    """
    db_conn = sqlite3.connect(db_file, isolation_level=isolation_level)
    try:
        with closing(db_conn.cursor()) as db_cursor:
            course_db = CourseDb(db_cursor)
            yield course_db
    except:
        db_conn.rollback()
        raise
    else:
        db_conn.commit()
    finally:
        db_conn.close()


def create_db_tables(db_file):
    """Create vmchecker's tables inside the given db_file"""
    with opening_course_db(db_file) as course_db:
        course_db.create_tables()
