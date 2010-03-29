#!/usr/bin/env python
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

import os
import time
import sqlite3

from . import paths
from . import repo_walker
from . import submissions
from . import penalty
from . import vmlogging
from .paths import VmcheckerPaths
from .config import CourseConfig
from .courselist import CourseList

logger = vmlogging.create_module_logger('update_db')



class CourseDb(object):
    """A class to encapsulate the logic behind updates and querries of
    the course's db"""

    def __init__(self, db_cursor):
        self.db_cursor = db_cursor

    def add_assignment(self, assignment):
        """Creates an id of the homework and returns it."""
        self.db_cursor.execute('INSERT INTO assignments (name) values (?)', (assignment,))
        self.db_cursor.execute('SELECT last_insert_rowid()')
        assignment_id, = self.db_cursor.fetchone()
        return assignment_id


    def get_assignment_id(self, assignment):
        """Returns the id of the assignment"""
        self.db_cursor.execute('SELECT id FROM assignments WHERE name=?', (assignment,))
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




class UpdateDb(repo_walker.RepoWalker):
    def __init__(self, vmcfg):
        repo_walker.RepoWalker.__init__(self, vmcfg)



    def _get_grade_value(self, vmcfg, assignment, user, grade_path):
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
                    vmcfg.get('vmchecker','PenaltyWeights').split()]

        limit = vmcfg.get('vmchecker','PenaltyLimit')
        sss = submissions.Submissions(VmcheckerPaths(vmcfg.root_path()))
        upload_time = sss.get_upload_time_str(assignment, user)

        deadline = time.strptime(vmcfg.assignments().get(assignment, 'Deadline'),
                                                penalty.DATE_FORMAT)
        holidays = int(vmcfg.get('vmchecker','Holidays'))

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
            holiday_start = vmcfg.get('vmchecker', 'HolidayStart').split(' , ')
            holiday_finish = vmcfg.get('vmchecker', 'HolidayFinish').split(' , ')
            penalty_value = penalty.compute_penalty(upload_time, deadline, 1 ,
                                weights, limit, holiday_start, holiday_finish)[0]
        else:
            penalty_value = penalty.compute_penalty(upload_time, deadline, 1 ,
                                weights, limit)[0]

        grade -= penalty_value
        return grade

    def _update_grades(self, vmcfg, force, assignment, user, grade_filename, course_db):
        """Updates grade for user's submission of assignment.

        Reads the grade's value only if the file containing the
        value was modified since the last update of the DB for this
        submission.

        """
        assignment_id = course_db.get_assignment_id(assignment)
        user_id = course_db.get_user_id(user)
        db_mtime = course_db.get_grade_mtime(assignment_id, user_id)

        mtime = os.path.getmtime(grade_filename)

        if force or db_mtime != mtime:
            # modified since last db save
            grade_value = self._get_grade_value(vmcfg, assignment, user, grade_filename)
            # updates information from DB
            course_db.save_grade(assignment_id, user_id, grade_value, mtime)

    def update_db(self, options, course_db):
        def _update_grades_wrapper(assignment, user, location, course_db, options):
            """A wrapper over _update_grades to use with repo_walker"""
            sbroot = self.vmpaths.dir_submission_root(assignment, user)
            grade_filename = paths.submission_results_grade(sbroot)
            if os.path.exists(grade_filename):
                self._update_grades(self.vmcfg, options, assignment, user, grade_filename, course_db)
                logger.info('Updated %s, %s (%s)', assignment, user, location)
            else:
                logger.error('No results found for %s, %s (check %s)',
                             assignment, user, grade_filename)

        # call the base implemnetation in RepoWalker.
        self.walk(options, _update_grades_wrapper, args=(course_db, options))




def update_all(course_id):
    """Walk all submissions"""
    class stupid_hack_class:
        """We only need this because repo_walker takes an object
        from cmdline directly. Repo_walker must be refactored."""
        def __init__(self, course_id):
            """Repo_walker needs a field named 'all' set to True
            in the object to be able to walk all assignments"""
            self.all = True
            self.recursive = False
            self.user = None
            self.assignment = None
            self.ignore_errors = False
            self.course_id = course_id
            self.simulate = False


    vmcfg = CourseConfig(CourseList().course_config(course_id))
    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())

    # open Db
    db_conn = sqlite3.connect(vmpaths.db_file(), isolation_level="EXCLUSIVE")
    db_cursor = db_conn.cursor()
    course_db = CourseDb(db_cursor)

    try:
        # actual work: update according to options the db
        options = stupid_hack_class(course_id)
        u = UpdateDb(vmcfg)
        u.update_db(options, course_db)
    finally:
        db_cursor.close()
        db_conn.commit() ## TODO:XXX: check if this should be commit
                         ## or rollback or whatever
        db_conn.close()
