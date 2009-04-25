#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Handles assignments and assignments options"""

import logging
import os

import vmcheckerpaths


# the prefix of the sections' names describing assignments
_SECTION_PREFIX = 'assignment '
_INCLUDE_PREFIX = 'include '
_DEFAULT = 'DEFAULT'

_logger = logging.getLogger('assignments')

_assignments = None     # the list of assignments


class Assignments(object):
    def __init__(self, config):
        """Returns the assignments from the RawConfigParser object, `config'"""
        self.__assignments = {}
        default = {}

        for section in config.sections():
            if section.startswith(_SECTION_PREFIX):
                assignment = section[len(_SECTION_PREFIX):]
                if assignment == _DEFAULT:
                    default = config.items(section)
                else:
                    self.__assignments[assignment] = config.items(section)

        default = dict(default)
        for assignment, items in self.__assignments.iteritems():
            temp = default.copy()
            temp.update(items)
            self.__assignments[assignment] = temp

    def write(self, assignment, config):
        """Dumps assigment's options to config"""
        items = self.__assignments[assignment]
        section = _SECTION_PREFIX + assignment

        config.add_section(section)
        for option, value in items:
            config.set(section, option, value)

    def include(self, assignment):
        """An iterator over the files to include when submitting an assignment.

        The iterators yields pairs (destination, source) where
            destination is the name of the file in the archive
            source is the name of the file on the disk relative to vmchecker root

        The include options is useful to include other scripts
        and configuration files.

        """
        for option in self.__assignments[assignment]:
            if option.startswith(_INCLUDE_PREFIX):
                yield (option[len(_INCLUDE_PREFIX):],
                       vmcheckerpaths.abspath(self.get(assignment, option)))

    def get(self, assignment, option):
        """Returns value of `option' for `assignment'.

        NOTE: section's name (thus assignment's name) is
        case-sensitive while option is case-insensitive.
        
        """
        return self.__assignments[assignment][option.lower()]

    def __iter__(self):
        """Returns an iterator over the assignments"""
        return iter(self.__assignments)

    def __contains__(self, assignment):
        """Returns True if `assignment' is a valid assignment"""
        return assignment in self.__assignments

    def course(self, assignment):
        assert assignment in self.__assignments, (
                'No such assignment %s' % repr(assignment))
        return self.get(assignment, 'course')

    def tests(self, assignment):
        assert assignment in self.__assignments, (
                'No such assignment %s' % repr(assignment))
        return os.path.join(vmcheckerpaths.dir_tests(), assignment + '.zip')
