#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-


from __future__ import with_statement

__author__ = 'Alexandru Moșoi <brtzsnr@gmail.com>'


import fcntl
import os
import socket
import struct
import ConfigParser

import vmcheckerpaths


DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

_config = None
_tester_config = None


def config_reader(config_file):
    """Returns a RawConfigParser for the speciffied file."""
    config = ConfigParser.RawConfigParser()
    with open(config_file) as handle:
        config.readfp(handle)
    return config


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
    conf_reader = config_reader(config_file)
    l = conf_reader.items(section_name)
    return dict(l)


def tester_config():
    """Returns a RawConfigParser containing vmchecker tester's configuration."""
    global _tester_config
    if _tester_config is None:
        _tester_config = ConfigParser.RawConfigParser()
        with open(vmcheckerpaths.tester_config_file()) as handle:
            _tester_config.readfp(handle)
    return _tester_config


def relative_path(*args):
    """Joins the arguments and returns a path relative to root"""
    return os.path.join(vmcheckerpaths.root(), os.path.join(*args))


def repository(assignment):
    """Returns repository where sources for assignment are stored.
 
    NOTE: Full path where they are actually stored is
    `repository/assignment'
    """
    return relative_path(config().get(assignment, 'Repository'))


def get_ip_address(ifname):
    """Returns ip address for network interface 'ifname'
    in standard dotted notation.

    Source from:
        http://code.activestate.com/recipes/439094/
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])

