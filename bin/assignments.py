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
_INCLUDE_PREFIX = 'include '
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


def include(assignment):
    """An iterator over the files to include when submitting an assignment.

    The iterators yields pairs (destination, source) where
        destination is the name of the file in the archive
        source is the name of the file on the disk relative to vmchecker root

    The include options is useful to include other scripts
    and configuration files.

    """
    for option in options(assignment):
        if option.startwith(_INCLUDE_PREFIX):
            yield (option[len(_INCLUDE_PREFIX):],
                   vmcheckerpaths.abspath(get(assignment, option)))


def get(assignment, option):
    """Gets `option' of `assignment'"""
    try:
        assert assignment.lower() != 'default'
        return config.get(_SECTION_PREFIX + assignment, option)
    except ConfigParser.NoOptionError:
        return config.get(_DEFAULT_SECTION, option)


def options(assignment):
    """Returns a set of options of assignment."""
    opts = set()
    opts.update(config.config.options(_SECTION_PREFIX + assignment))
    opts.update(config.config.options(_DEFAULT_SECTION))
    return opts


def path(assignment, option):
    """Similar to get, but returns a path"""
    return os.path.join(vmcheckerpaths.root,
                        get(assignment, option))

