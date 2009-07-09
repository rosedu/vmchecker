#!/usr/bin/env python

import unittest

from vmchecker import sql, courses, VmcheckerError


class TestCourses(unittest.TestCase):
    def setUp(self):
        sql.clear_tables()

    def testsimple(self):
        name = 'nothing'
        id = courses.create(name)
        print id
        self.assert_(id is not None)
        self.assertEqual(name, courses.get(id).name)

    def testduplicate(self):
        name = 'skip'
        courses.create(name)
        self.assertRaises(VmcheckerError, courses.create, name)


if __name__ == '__main__':
    unittest.main()
