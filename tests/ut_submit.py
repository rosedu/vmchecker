#!/usr/bin/env python

import datetime
import os
import tempfile
import unittest

from vmchecker import sql, submit


COURSE_NAME = 'Sisteme de Operare'

ASSIGNMENT_NAME = '1-minishell-linux'
URL = 'http://somewhere.in.the.dark/text.html'
repository = tempfile.mkdtemp()
DEADLINE = datetime.datetime(2009, 7, 6, 17, 58, 36)
TIMEOUT = 666
MAXGRADE = 117

USERNAME = 'lgrijincu'
FULLNAME = 'Lucian Adrian Grijincu'


class TestSubmit(unittest.TestCase):
    def setUp(self):
        """Creates a course, an assignment, and an user"""
        sql.connect('mysql://root:alfabet@localhost/vmchecker')
        sql.clear_tables()

        # creates a course
        insert = sql.courses.insert().values(
                name = COURSE_NAME)
        self.course_id = sql.connection.execute(insert).last_inserted_ids()[0]

        # creates an assignment
        insert = sql.assignments.insert().values(
                course_id = self.course_id,
                name = ASSIGNMENT_NAME,
                url = URL,
                repository = repository,
                deadline = DEADLINE,
                timeout = TIMEOUT,
                maxgrade = MAXGRADE)
        self.assignment_id = sql.connection.execute(insert).last_inserted_ids()[0]

        # creats an user
        insert = sql.users.insert().values(
                username = USERNAME,
                fullname = FULLNAME)
        self.user_id = sql.connection.execute(insert).last_inserted_ids()[0]

    def testsubmit(self):
        submission_id, path = submit.store(
                __file__,
                self.assignment_id,
                self.user_id)

        with open(os.path.join(path, submit.SOURCES_FILE)) as f1:
            with open(__file__) as f2:
                self.assertEqual(f1.read(), f2.read())


if __name__ == '__main__':
    unittest.main()
