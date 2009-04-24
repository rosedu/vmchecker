#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Handles assignments and assignments options"""


import ConfigParser
import logging
import os

import config
import vmcheckerpaths


# the prefix of the sections' names describing assignments
_SECTION_PREFIX = 'assignment '
_DEFAULT_SECTION = _SECTION_PREFIX + 'DEFAULT'

_logger = logging.getLogger('assignments')

_assignments = None     # the list of assignments


def assignments():
    """Returns the sorted list of assignments"""
    global _assignments
    if _assignments is None:
        _assignments = []

        for section in config.config.sections():
            if section.startswith(_SECTION_PREFIX):
                assignment = section[len(_SECTION_PREFIX):]
                _assignments.append(assignment)

        _assignments.sort()
        _logger.debug('Found assignments %s', _assignments)

    return _assignments


def get(assignment, option):
    """Gets `option' of `assignment'"""
    try:
        assert assignment.lower() != 'default'
        return config.get(_SECTION_PREFIX + assignment, option)
    except ConfigParser.NoOptionError:
        return config.get(_DEFAULT_SECTION, option)


def path(assigment, option):
    """Similar to get, but returns a path"""
    return os.path.join(vmcheckerpaths.root,
                        get(assigment, option))

