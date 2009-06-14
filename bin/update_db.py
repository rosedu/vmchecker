#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Updates marks for modified results

For reference below is the (possible outdated) database schema.
For the latest version check bin/initialise_course.py.

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

"""

from __future__ import with_statement

import sqlite3
import os
import optparse
import logging

import config
import vmcheckerpaths
import repo_walker

import time

import submissions
import penalty

_logger = logging.getLogger('update_db')

def _db_save_assignment(db_cursor, assignment):
    """Creates an id of the homework and returns it."""
    db_cursor.execute('INSERT INTO assignments (name) values (?)',
                      (assignment,))
    db_cursor.execute('SELECT last_insert_rowid()')
    assignment_id, = db_cursor.fetchone()
    return assignment_id


def _db_get_assignment_id(db_cursor, assignment):
    """Returns the id of the assignment"""
    db_cursor.execute('SELECT id FROM assignments WHERE name=?', (assignment,))
    result = db_cursor.fetchone()
    if result is None:
        return _db_save_assignment(db_cursor, assignment)
    return result[0]


def _db_save_user(db_cursor, user):
    """Creates an id of the user and returns it."""
    db_cursor.execute('INSERT INTO users (name) values (?)', (user,))
    db_cursor.execute('SELECT last_insert_rowid()')
    user_id, = db_cursor.fetchone()
    return user_id


def _db_get_user_id(db_cursor, user):
    """Returns the id of the user"""
    db_cursor.execute('SELECT id FROM users WHERE name=?', (user,))
    result = db_cursor.fetchone()
    if result is None:
        return _db_save_user(db_cursor, user)
    return result[0]


def _db_get_grade_mtime(db_cursor, assignment_id, user_id):
    """Returns the mtime of a grade"""
    db_cursor.execute(
            'SELECT mtime FROM grades '
            'WHERE assignment_id = ? and user_id = ?', (
                assignment_id, user_id))

    result = db_cursor.fetchone()
    if result is not None:
        return result[0]


def _db_save_grade(db_cursor, assignment_id, user_id, grade, mtime):
    """Saves the grade into the database

    If the grade identified by (assignment_id, user_id)
    exists then update the DB, else inserts a new entry.

    """
    db_cursor.execute(

        'INSERT OR REPLACE INTO grades (grade, mtime, assignment_id, user_id) '
        'VALUES (?, ?, ?, ?) ', (grade, mtime, assignment_id, user_id))


def _get_grade_value(assignment, user, grade_path):
    """Returns the grade value after applying penalties and bonuses.

    Computes the time penalty for the user, obtains the other
    penalties and bonuses from the grade_path file
    and computes the final grade.

    The grade_path file can have any structure.
    The only rule is the following: any number that starts with '-'
    or '+' is taken into account when computing the grade.

    An example for the file:
        +0.1 very good comments
        -0.2  possible leak of memory on line 234 +0.1 treats exceptions
        -0.2 use of magic numbers
    """

    weights = [float(x) for x in
                config.get('vmchecker','PenaltyWeights').split()]

    limit = config.get('vmchecker','PenaltyLimit')

    upload_time = submissions.get_upload_time_str(assignment, user)

    deadline = time.strptime(config.assignments.get(assignment, 'Deadline'),
                                            penalty.DATE_FORMAT)
    holidays = int(config.get('vmchecker','Holidays'))

    grade = 10
    words = 0
    word = ""

    with open(grade_path) as handler:
        for line in handler.readlines():
            for word in line.split():
                words += 1
                if word[0] in ['+','-']:
                    try:
                        grade += float(word)
                    except ValueError:
                        pass

    #word can be either 'copiat' or 'ok'
    if words == 1:
        return word

    #at this point, grade is <= 0 if the homework didn't compile
    if grade <= 0:
        return 0

    if holidays != 0:
        holiday_start = config.get('vmchecker', 'HolidayStart').split(' , ')
        holiday_finish = config.get('vmchecker', 'HolidayFinish').split(' , ')
        penalty_value = penalty.compute_penalty(upload_time, deadline, 1 , 
                            weights, limit, holiday_start, holiday_finish)[0]
    else:
        penalty_value = penalty.compute_penalty(upload_time, deadline, 1 ,
                            weights, limit)[0]

    grade -= penalty_value
    return grade

def _update_grades(assignment, user, grade_filename, db_cursor):
    """Updates grade for user's submission of assignment.

    Reads the grade's value only if the file containing the
    value was modified since the last update of the DB for this
    submission.

    """
    assignment_id = _db_get_assignment_id(db_cursor, assignment)
    user_id = _db_get_user_id(db_cursor, user)

    mtime = os.path.getmtime(grade_filename)
    db_mtime = _db_get_grade_mtime(db_cursor, assignment_id, user_id)

    if config.options.force or db_mtime != mtime:
        # modified since last db save
        grade_value = _get_grade_value(assignment, user, grade_filename)
        # updates information from DB
        _db_save_grade(db_cursor, assignment_id, user_id, grade_value, mtime)


def main():
    """Checks for modified grades and updates the database"""
    config.config_storer()

    db_conn = sqlite3.connect(vmcheckerpaths.db_file(),
                              isolation_level="EXCLUSIVE")
    db_cursor = db_conn.cursor()

    def _update_grades_wrapper(assignment, user, location, db_cursor):
        """A wrapper over _update_grades to use with repo_walker"""
        grade_filename = os.path.join(location, vmcheckerpaths.GRADE_FILENAME)
        if os.path.exists(grade_filename):
            _update_grades(assignment, user, grade_filename, db_cursor)
            _logger.info('Updated %s, %s (%s)', assignment, user, location)
        else:
            _logger.error('No results found for %s, %s (check %s)',
                          assignment, user, grade_filename)

    repo_walker.walk(_update_grades_wrapper, args=(db_cursor,))

    db_cursor.close()
    db_conn.commit()
    db_conn.close()


group = optparse.OptionGroup(config.cmdline, 'update_db.py')
group.add_option(
        '-f', '--force', action='store_true', dest='force', default=False,
        help='Force updating all marks ignoring modification times')
config.cmdline.add_option_group(group)
del group


if __name__ == '__main__':
    main()

