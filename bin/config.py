#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-
"""General configuration module"""


from __future__ import with_statement

import os
import optparse
import logging
import ConfigParser

import vmcheckerpaths


DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

cmdline = optparse.OptionParser()
options, args = None, None

config = ConfigParser.RawConfigParser()


def parse_arguments():
    """Parses command-line arguments"""
    global options, args
    options, args = cmdline.parse_args()


def _basic_config():
    """Common configuration"""

    # sets root path
    assert 'VMCHECKER_ROOT' in os.environ, (
            'Environment variable $VMCHECKER_ROOT is not defined')
    vmcheckerpaths.root = os.path.abspath(os.environ['VMCHECKER_ROOT'])

    # sets logging
    logging.basicConfig(level=logging.INFO)

    # parse command-line arguments
    parse_arguments()


def config_storer():
    """Configures storer"""
    _basic_config()

    with open(vmcheckerpaths.storer_config_file()) as handle:
        config.readfp(handle)

    # sets repository path
    vmcheckerpaths.repository = path('DEFAULT', 'Repository')


def config_tester():
    """Configures tester"""
    _basic_config()
    with open(vmcheckerpaths.tester_config_file()) as handle:
        config.readfp(handle)


def get(*args):
    """A convenient wrapper for config.get(), .options() and .sections()"""
    if len(args) == 0:
        return config.sections()
    if len(args) == 1:
        return config.options(args[0])
    if len(args) == 2:
        return config.get(args[0], args[1])
    assert False


def path(section, option):
    """Returns an absolute path derived from an option"""
    return vmcheckerpaths.abspath(config.get(section, option))


def _set_logging_level(option, opt_str, value, parser):
    """Sets the logging level throu command-line arguments"""
    setattr(parser.values, option.dest, True)

    if option.dest == 'verbose':
        logging.getLogger().setLevel(logging.DEBUG)
    if option.dest == 'quiet':
        logging.getLogger().setLevel(logging.WARN)


def assignments():
    """Returns a list of assigments"""
    return list(config.sections())


cmdline.add_option('-v', '--verbose', action='callback', nargs=0,
                   dest='verbose', default=False, callback=_set_logging_level,
                   help='Prints more stuff')
cmdline.add_option('-q', '--quiet', action='callback', nargs=0,
                   dest='quiet', default=False, callback=_set_logging_level,
                   help='Prints less stuff')
