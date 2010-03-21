#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General configuration module"""


from __future__ import with_statement

import os
import ConfigParser

from . import assignments


DATE_FORMAT = '%Y.%m.%d %H:%M:%S'


class CourseConfig:
    """An object that encapsulates parsing of the config file of a course"""
    def __init__(self, config_file_):
        self.config_file = config_file_
        self.config = ConfigParser.RawConfigParser()
        with open(os.path.expanduser(config_file_)) as handle:
            self.config.readfp(handle)

    def get(self, section, option):
        """A convenient wrapper for config.get()"""
        return self.config.get(section, option)

    def repository_path(self):
        """Get the submission (git) repository path for this course."""
        return self.config.get('vmchecker', 'repository')

    def sections(self):
        """Give access to the underlining config's sections"""
        # XXX: LAG: I think this is a sign that we should have derived the
        # RawConfigParser class.
        return self.config.sections()

    def root_path(self):
        """Get the root path for this course"""
        return self.config.get('vmchecker', 'root')

    def storer_username(self):
        """The username to use when logging in with ssh to the storer machine"""
        return self.config.get('storer', 'username')

    def tester_username(self):
        """The username to use when logging in with ssh to the tester machine"""
        return self.config.get('tester', 'username')

    def storer_hostname(self):
        """The hostname to use when logging in with ssh to the storer machine"""
        return self.config.get('storer', 'hostname')

    def tester_hostname(self):
        """The hostname to use when logging in with ssh to the tester machine"""
        return self.config.get('tester', 'hostname')

    def tester_queue_path(self):
        """The path on the tester machine where the queued files are put"""
        return self.config.get('tester', 'queuepath')

    def assignments(self):
        """Return an Assignment object describing the assignments in
        this course's config file"""
        return assignments.Assignments(self)
