#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General configuration module"""


from __future__ import with_statement

import os
import optparse
import logging
import ConfigParser

import vmcheckerpaths
import assignments as assignments_
from assignments import _SECTION_PREFIX

DATE_FORMAT = '%Y.%m.%d %H:%M:%S'
DEFAULT_CONFIG_FILE = '/tmp/tmp/config'

cmdline = optparse.OptionParser()
options, argv = None, None

# Use OptionGroup to add commandline options. Here is an example:
#
# import config
#
# ... (at the end of the file)
#
# group = optparse.OptionGroup(config.cmdline, 'update_db.py')
# group.add_option(
#         '-f', '--force', action='store_true', dest='force', default=False,
#         help='Force updating all marks ignoring modification times')
# config.cmdline.add_option_group(group)
# del group

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

    def assignments(self):
        """Return an Assignment object describing the assignments in
        this course's config file"""
        return assignments_.Assignments(self.config)


def parse_arguments():
    """Parses command-line arguments"""
    global options, argv
    options, argv = cmdline.parse_args()


def _basic_config():
    """Common configuration"""
    # sets logging
    logging.basicConfig(level=logging.INFO)
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



def _set_logging_level(option, opt_str, value, parser):
    """Sets the logging level throu command-line arguments"""
    setattr(parser.values, option.dest, True)

    if option.dest == 'verbose':
        logging.getLogger().setLevel(logging.DEBUG)
    if option.dest == 'quiet':
        logging.getLogger().setLevel(logging.WARN)


cmdline.add_option('-v', '--verbose', action='callback', nargs=0,
                   dest='verbose', default=False, callback=_set_logging_level,
                   help='Prints more stuff')
cmdline.add_option('-q', '--quiet', action='callback', nargs=0,
                   dest='quiet', default=False, callback=_set_logging_level,
                   help='Prints less stuff')
cmdline.add_option('--config', dest='config', default=DEFAULT_CONFIG_FILE,
                   metavar='FILE', help='Reads configuration from FILE ('
                                        'defaults to %s)' % DEFAULT_CONFIG_FILE)
