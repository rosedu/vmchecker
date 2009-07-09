#!/usr/bin/env python

import unittest

from vmchecker import sql, courses, VmcheckerError


class TestCourses(unittest.TestCase):
    def setUp(self):
        sql.clear_tables()

    def testsimple(self):
        name = 'nothing'
        id = courses.create(name = name)
        self.assert_(id is not None)
        course = courses.get(id)
        self.assertEqual(name, course.name)

    def testduplicate(self):
        name = 'skip'
        courses.create(name)
        self.assertRaises(VmcheckerError, courses.create, name = name)

    def testnull(self):
        self.assertRaises(VmcheckerError, courses.create, name = None)


if __name__ == '__main__':
    unittest.main()
