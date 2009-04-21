#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-
"""Vmchecker configuration file readers"""

from __future__ import with_statement

__author__ = 'Alexandru Moșoi <brtzsnr@gmail.com>'


import ConfigParser

import vmcheckerpaths


DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

_config = None
_tester_config = None


def config_reader(config_file):
    """Returns a RawConfigParser for the speciffied file."""
    config_ = ConfigParser.RawConfigParser()
    with open(config_file) as handle:
        config_.readfp(handle)
    return config_


def config():
    """Returns a RawConfigParser containing vmchecker's configuration."""
    global _config
    if _config is None:
        _config = config_reader(vmcheckerpaths.config_file())
    return _config


def config_variables(config_file, section_name):
    """Return a dictionary with values from the config_path file.

    NB:  the keys will be all lowercase!

    """
    config_ = config_reader(config_file)
    return dict(config_.items(section_name))


def tester_config():
    """Returns a RawConfigParser with vmchecker tester's configuration."""
    global _tester_config
    if _tester_config is None:
        _tester_config = ConfigParser.RawConfigParser()
        with open(vmcheckerpaths.tester_config_file()) as handle:
            _tester_config.readfp(handle)
    return _tester_config



def repository():
    """Returns repository path"""
    return vmcheckerpaths.abspath(config().get('DEFAULT', 'Repository'))
