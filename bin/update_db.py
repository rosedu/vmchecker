#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-
"""Updates marks for modified results"""

from __future__ import with_statement

__author__ = 'Gheorghe Claudiu-Dan <claudiugh@gmail.com>'

import sqlite3
import os
import time
import optparse
import logging

import misc
import config
import vmcheckerpaths
import repo_walker


_GRADE_VALUE_FILE = 'results/job_results'

_logger = logging.getLogger('update_db')
db_cursor = None


def _db_get_hw(hw_name):
    """ Get a homework entry

    @return the id of the homework or None if it doesn't exist

    """
    db_cursor.execute('SELECT id FROM teme WHERE nume = ?;', (hw_name,))
    result = db_cursor.fetchone()
    if result is not None:
        return result[0]


def _db_save_hw(hw_name):
    """ If the homework identified by (hw_name)
    exists then update the DB, else insert a new entry """

    assigment = _db_get_hw(hw_name)
    if assigment is None:
        db_cursor.execute('INSERT INTO teme (nume) values (?)', (hw_name,))
        db_cursor.execute('SELECT last_insert_rowid();')
        assigment, = db_cursor.fetchone()

    return assigment


def _db_get_student(student_name):
    """ Get a student entry

    @return the id of the entry or None if the entry doesn't exist

    """
    db_cursor.execute('SELECT id FROM studenti WHERE nume = ?;',
                      (student_name,))
    result = db_cursor.fetchone()
    if result is not None:
        return result[0]


def _db_save_student(student_name):
    """ If the student identified by (student_name)
    exists then update the DB, else insert a new entry """
    id_student = _db_get_student(student_name)
    if None == id_student:
        db_cursor.execute('INSERT INTO studenti (nume) values (?)',
                          (student_name,))
        db_cursor.execute('SELECT last_insert_rowid();')
        id_student, = db_cursor.fetchone()
    return id_student


def _db_get_grade(assigment, id_student):
    """ Get a grade entry
    @return
     - a touple containing the id and the last modification timestamp
     - (None, None) if it doesn't exist """
    db_cursor.execute(
            'SELECT id, data FROM note WHERE id_tema = ? and id_student = ?;',
            (assigment, id_student))
    result = db_cursor.fetchone()
    if None == result:
        return (None, None)
    else:
        return result


def _db_save_grade(assigment, id_student, grade, data):
    """If the grade identified by (assigment, id_student)
    exists then update the DB, else insert a new entry"""
    id_grade, db_data = _db_get_grade(assigment, id_student)
    if id_grade is None:
        db_cursor.execute(
                'INSERT INTO note (id_tema, id_student, nota, data) values (?, ?, ?, ?)',
                (assigment, id_student, grade, data ))
    else:
        db_cursor.execute(
                'UPDATE note set nota = ?, data = ? where id = ?',
                (grade, data, id_grade))


def update_hws(path):
    """ For each dentry from path, launch the next
    level update routine - update_students() """
    for hw_name in os.listdir(path):
        path_hw = os.path.join(path, hw_name)
        if hw_name[0] != '.' and os.path.isdir(path_hw):
            # save hw in the DB
            assigment = _db_save_hw(hw_name)
            update_students(path_hw, assigment)


def update_students(path, assigment):
    """For each dentry from path, launch the update_grade() routine"""
    for student_name in os.listdir(path):
        path_student = os.path.join(path, student_name)
        if student_name[0] != '.' and os.path.isdir(path_student):
            # save student in the DB
            id_student = _db_save_student(student_name)
            update_grade(path_student, assigment, id_student)


def grade_modification_time(grade_filename):
    """Returns the modification time for file named `grade_filename'"""
    return time.strftime(config.DATE_FORMAT,
            time.gmtime(os.path.getmtime(grade_filename)))


def get_grade_value(grade_filename):
    """Reads an integer from the first line of the file.

    XXX A string should actually be read (eg: ok, copied)

    """
    with open(grade_filename) as handler:
        try:
            return int(handler.readline())
        except ValueError:
            return -1


def update_grade(assigment, user, location):
    """Reads the grade's value only if the file containing the
    value was modified since the last update of the DB for this
    submission.

    """
    grade_filename = os.path.join(location, _GRADE_VALUE_FILE)
    if not os.path.exists(grade_filename):
        _logger.error('No results found for %s, %s (%s)',
                assigment, user, location)
        return None

    data_modif = grade_modification_time(grade_filename)
    id_grade, db_data = _db_get_grade(assigment, user)

    if config.options.force or db_data != data_modif:
        # modified since last db save
        grade_value = get_grade_value(grade_filename)
        if None != grade_value:
            # updates information from DB
            _db_save_grade(assigment, user, grade_value, data_modif)
            _logger.info('Updated %s, %s (%s)', assigment, user, location)


def main():
    config.config_storer()
    logging.basicConfig(level=logging.DEBUG)

    db_conn = sqlite3.connect(vmcheckerpaths.db_file())
    db_conn.isolation_level = None  # autocommits updates

    global db_cursor  # XXX make local and pass throu arguments
    db_cursor = db_conn.cursor()

    repo_walker.walk(update_grade)

    db_cursor.close()
    db_conn.close()


group = optparse.OptionGroup(config.cmdline, 'update_db.py', '')
group.add_option(
        '-f', '--force', action='store_true', dest='force', default=False,
        help='Updates marks ignoring results modifications')
config.cmdline.add_option_group(group)
del group


if __name__ == '__main__':
    main()

