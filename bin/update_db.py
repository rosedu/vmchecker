#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

from __future__ import with_statement

__author__ = 'Gheorghe Claudiu-Dan <claudiugh@gmail.com>'

import sqlite3
import os
import time
import stat
import logging

import misc
import vmcheckerpaths


_logger = logging.getLogger("vmchecker.update_db")

GRADE_VALUE_FILE = 'nota'


def DB_get_hw(hw_name):
    """ Get a homework entry
    @return
     - the id of the homework
     - None if it doesn't exist """
    global db_cursor
    db_cursor.execute('SELECT id FROM teme WHERE nume = ?;', (hw_name,))
    result = db_cursor.fetchone()
    if None == result:
        return result
    else:
        return result[0]


def DB_save_hw(hw_name):
    """ If the homework identified by (hw_name)
    exists then update the DB, else insert a new entry """
    global db_cursor

    id_hw = DB_get_hw(hw_name)
    if None == id_hw:
        db_cursor.execute('INSERT INTO teme (nume) values (?)', (hw_name,))
        db_cursor.execute('SELECT last_insert_rowid();')
        (id_hw,) = db_cursor.fetchone()

    return id_hw


def DB_get_student(student_name):
    """ Get a student entry
    @return
     - the id of the entry
     - None if it doesn't exist """
    global db_cursor
    db_cursor.execute('SELECT id FROM studenti WHERE nume = ?;', (student_name,))
    result = db_cursor.fetchone()
    if result is None:
        return result
    else:
        return result[0]


def DB_save_student(student_name):
    """ If the student identified by (student_name)
    exists then update the DB, else insert a new entry """
    global db_cursor
    id_student = DB_get_student(student_name)
    if None == id_student:
        db_cursor.execute('INSERT INTO studenti (nume) values (?)', (student_name,))
        db_cursor.execute('SELECT last_insert_rowid();')
        (id_student,) = db_cursor.fetchone()
    return id_student


def DB_get_grade(id_hw, id_student):
    """ Get a grade entry
    @return
     - a touple containing the id and the last modification timestamp
     - (None, None) if it doesn't exist """
    global db_cursor
    db_cursor.execute('SELECT id, data FROM note WHERE id_tema = ? and id_student = ?;', (id_hw, id_student))
    result = db_cursor.fetchone()
    if None == result:
        return (None, None)
    else:
        return result


def DB_save_grade(id_hw, id_student, grade, data):
    """ If the grade identified by (id_hw, id_student)
    exists then update the DB, else insert a new entry """
    global db_cursor
    (id_grade, db_data) = DB_get_grade(id_hw, id_student)
    if None == id_grade:
        db_cursor.execute('INSERT INTO note (id_tema, id_student, nota, data) values (?, ?, ?, ?)', (id_hw, id_student, grade, data ))
    else:
        db_cursor.execute('UPDATE note set nota = ?, data = ? where id = ?', (grade, data, id_grade))


def update_hws(path):
    """ For each dentry from path, launch the next
    level update routine - update_students() """
    for hw_name in os.listdir(path):
        path_hw = os.path.join(path, hw_name)
        if path_hw[0] != '.' and os.path.isdir(path_hw):
            # save hw in the DB
            id_hw = DB_save_hw(hw_name)
            update_students(path_hw, id_hw)


def update_students(path, id_hw):
    """For each dentry from path, launch the update_grade() routine"""
    for student_name in os.listdir(path):
        path_student = os.path.join(path, student_name)
        if path_student[0] != '.' and os.path.isdir(path_student):
            # save student in the DB
            id_student = DB_save_student(student_name)
            update_grade(path_student, id_hw, id_student)


def grade_modification_time(grade_filename):
    return time.strftime(misc.DATE_FORMAT, time.gmtime(os.path.getmtime(grade_filename)))


def get_grade_value(grade_filename):
    """ read an integer from the first line of the file """
    with open(grade_filename, 'r') as f:
        try:
            return int(f.readline())
        except ValueError:
            return -1


def update_grade(path, id_hw, id_student):
    """Reads the grade's value only if the file containing the
    value was modified since the last update of the DB for this
    submission."""
    grade_filename = os.path.join(path, GRADE_VALUE_FILE)
    if not os.path.exists(grade_filename):
        _logger.error("File [%s] for grade value does not exist " % grade_filename)
        return None
    data_modif = grade_modification_time(grade_filename)
    (id_grade, db_data) = DB_get_grade(id_hw, id_student)
    if db_data != data_modif:
        # modified since last db save
        grade_value = get_grade_value(grade_filename)
        if None != grade_value:
            # update information from DB
            DB_save_grade(id_hw, id_student, grade_value, data_modif)
            print path, " UPDATED "


def main():
    # determine the level
    LEVEL_HWS = 0
    LEVEL_STUDENTI = 1
    LEVEL_GRADE = 2

    path = os.getcwd()
    level = LEVEL_HWS
    while path != misc.repository():
        (path, tail) = os.path.split(path)
        level = level + 1

    if level == LEVEL_HWS:
        update_hws(os.getcwd())
    elif level == LEVEL_STUDENTI:
        # get the name for homework
        (head, nume_hw) = os.path.split(os.getcwd())
        # get the id
        id_hw = DB_save_hw(nume_hw)
        update_students(os.getcwd(), id_hw)
    elif level == LEVEL_GRADE:
        # get the  names from the path
        (head, nume_student) = os.path.split(os.getcwd())
        (head, nume_hw) = os.path.split(head)
        # get the DB identifiers
        id_hw = DB_save_hw(nume_hw)
        id_student = DB_save_student(nume_student)
        update_grade(os.getcwd(), id_hw, id_student)

        db_cursor.close()
        db_conn.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if not os.getcwd().startswith(misc.repository()):
        _logger.error("Error: working directory `%s' not in the repository `%s' subtree.",
                     os.getcwd(), misc.repository())
        exit(1)

    if not os.path.isfile(vmcheckerpaths.db_file()):
        _logger.error("Error: DB file [%s] doesn't exist", vmcheckerpaths.db_file())
        exit(1)

    # TODO: rename for better encapsulation
    global db_conn, db_cursor
    db_conn = sqlite3.connect(vmcheckerpaths.db_file())
    db_conn.isolation_level = None  # this is for autocommiting updates
    db_cursor = db_conn.cursor()

    main()
