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
DEFAULT_CONFIG_FILE = '~/.vmcheckerrc'

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

config = ConfigParser.RawConfigParser()
assignments = None


def vmcheckerrc_path():
    """Returns the path to the .vmcheckerrc file

    This respects the user's choice through the '--config'/'-c'
    commandline option. If no '--config'/'-c' was specified it uses
    DEFAULT_CONFIG_FILE.

    """
    return os.path.expanduser(options.config)

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
    assert os.path.isabs(vmcheckerrc_path())
    with open(vmcheckerrc_path()) as handle:
        config.readfp(handle)

    vmcheckerpaths.set_root(config.get('vmchecker', 'root'))


def config_storer():
    """Configures storer"""
    _basic_config()

    global assignments
    vmcheckerpaths.set_repository(config.get('vmchecker', 'repository'))
    assignments = assignments_.Assignments(config)


def config_tester():
    """Configures tester"""
    _basic_config()


def get(section, option):
    """A convenient wrapper for config.get()"""
    return config.get(section, option)


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
