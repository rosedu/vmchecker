#!/usr/bin/env python

import unittest
import tempfile
import shutil
import datetime

from vmchecker import sql, assignments, courses, VmcheckerError

COURSE_NAME = 'course'
NAME = 'assignment'
URL = 'http://somewhere.in.the.dark/text.html'
DEADLINE = datetime.datetime(2009, 7, 6, 17, 58, 36)
TIMEOUT = 666
MAXGRADE = 117


class TestCourses(unittest.TestCase):
    def setUp(self):
        sql.clear_tables()

        self.course_id = courses.create(COURSE_NAME)
        self.repository = tempfile.mkdtemp()

    def create_assignment(self, **kwargs):
        args = {
                'course_id': self.course_id,
                'name': NAME,
                'url': URL,
                'repository': self.repository,
                'deadline': DEADLINE,
                'timeout': TIMEOUT,
                'maxgrade': MAXGRADE
                }
        args.update(kwargs)
        return assignments.create(**args)

    def tearDown(self):
        shutil.rmtree(self.repository)

    def testsimple(self):
        id = self.create_assignment()
        self.assert_(id is not None)

        assignment = assignments.get(id)
        self.assertEqual(self.course_id, assignment.course_id)
        self.assertEqual(NAME, assignment.name)
        self.assertEqual(URL, assignment.url)
        self.assertEqual(self.repository, assignment.repository)
        self.assertEqual(DEADLINE, assignment.deadline)
        self.assertEqual(TIMEOUT, assignment.timeout)
        self.assertEqual(MAXGRADE, assignment.maxgrade)

    def testduplicate(self):
        id = self.create_assignment()
        self.assertRaises(VmcheckerError, self.create_assignment)


if __name__ == '__main__':
    unittest.main()
