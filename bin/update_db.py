#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Updates marks for modified results"""

from __future__ import with_statement

import sqlite3
import os
import optparse
import logging

import config
import vmcheckerpaths
import repo_walker


_logger = logging.getLogger('update_db')


def _db_save_assignment(db_cursor, assignment):
    """Creates an id of the homework and returns it."""
    db_cursor.execute('INSERT INTO assignments (name) values (?)',
                      (assignment,))
    db_cursor.execute('SELECT last_insert_rowid()')
    assignment_id, = db_cursor.fetchone()
    return assignment_id


def _db_get_assignment_id(db_cursor, assignment):
    """Returns the id of the assigment"""
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


def _db_get_grade(db_cursor, assignment_id, user_id):
    """Returns the id and the mtime of a grade"""
    db_cursor.execute(
            'SELECT id, mtime FROM grades '
            'WHERE assignment_id = ? and user_id = ?', (
                assignment_id, user_id))
    result = db_cursor.fetchone()
    if result is not None:
        return result[0], result[1]


def _db_get_grade_id(db_cursor, assignment_id, user_id):
    """Returns the id of a grade"""
    result = _db_get_grade(db_cursor, assignment_id, user_id)
    if result is not None:
        return result[0]


def _db_get_grade_mtime(db_cursor, assignment_id, user_id):
    """Returns the mtime of a grade"""
    result = _db_get_grade(db_cursor, assignment_id, user_id)
    if result is not None:
        return result[1]


def _db_save_grade(db_cursor, assignment_id, user_id, grade, mtime):
    """Saves the grade into the database

    If the grade identified by (assignment_id, user_id)
    exists then update the DB, else inserts a new entry.

    XXX should use ON DUPLICATE KEY UPDATE

    """
    grade_id = _db_get_grade_id(db_cursor, assignment_id, user_id)

    if grade_id is None:
        db_cursor.execute(
                'INSERT INTO grades (assignment_id, user_id, grade, mtime) '
                'VALUES (?, ?, ?, ?)', (
                    assignment_id, user_id, grade, mtime))
    else:
        db_cursor.execute(
                'UPDATE grades set grade = ?, mtime = ? where id = ?', (
                    grade, mtime, grade_id))


def _get_grade_value(grade_path):
    """Reads the first line of grade_path containing the grade."""
    with open(grade_path) as handler:
        return handler.readline().strip()


def _update_grades(assignment_id, user_id, grade_filename, db_cursor):
    """Updates grade for user's submission of assigment.

    Reads the grade's value only if the file containing the
    value was modified since the last update of the DB for this
    submission.

    """
    mtime = os.path.getmtime(grade_filename)
    db_mtime = _db_get_grade_mtime(db_cursor, assignment_id, user_id)

    if config.options.force or db_mtime != mtime:
        # modified since last db save
        grade_value = _get_grade_value(grade_filename)
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
        assignment_id = _db_get_assignment_id(db_cursor, assignment)
        user_id = _db_get_user_id(db_cursor, user)

        grade_filename = os.path.join(location, vmcheckerpaths.GRADE_FILENAME)
        if os.path.exists(grade_filename):
            _update_grades(assignment_id, user_id, grade_filename, db_cursor)
            _logger.info('Updated %s, %s (%s)', assignment, user, location)
        else:
            _logger.error('No results found for %s, %s (check %s)',
                          assignment, user, grade_filename)

    repo_walker.walk(_update_grades_wrapper, args=(db_cursor,))

    db_cursor.close()
    db_conn.close()


group = optparse.OptionGroup(config.cmdline, 'update_db.py')
group.add_option(
        '-f', '--force', action='store_true', dest='force', default=False,
        help='Force updating all marks ignoring modification times')
config.cmdline.add_option_group(group)
del group


if __name__ == '__main__':
    main()

