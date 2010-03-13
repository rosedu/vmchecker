#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General configuration module"""


from __future__ import with_statement

import os
import optparse
import ConfigParser

import vmcheckerpaths
import assignments as assignments_

DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

assignments = None

class VmcheckerConfig:
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
        return self.config.get('storer', 'username')

    def tester_username(self):
        return self.config.get('tester', 'username')

    def storer_hostname(self):
        return self.config.get('storer', 'hostname')

    def tester_hostname(self):
        return self.config.get('tester', 'hostname')

    def tester_queue_path(self):
        return self.config.get('tester', 'queuepath')

    def assignments(self):
        """Return an Assignment object describing the assignments in
        this course's config file"""
        return assignments_.Assignments(self)


def parse_arguments():
    """Parses command-line arguments"""
    global options, argv
    options, argv = cmdline.parse_args()


def _basic_config():
    """Common configuration"""
    parse_arguments()

    # reads configuration
    assert os.path.isabs(options.config)
    vmcfg = VmcheckerConfig(options.config)
    vmcheckerpaths.set_root(vmcfg.root_path())
    return vmcfg


def config_storer():
    """Configures storer"""
    vmcfg = _basic_config()

    global assignments
    vmcheckerpaths.set_repository(vmcfg.repository_path())
    assignments = vmcfg.assignments()
    return vmcfg


def config_tester():
    """Configures tester"""
    vmcfg = _basic_config()
    return vmcfg
