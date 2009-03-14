#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
# vim: set expandtab :


__author__ = 'Alexandru Mosoi <brtzsnr@gmail.com>'


import fcntl
import os
import socket
import struct

import ConfigParser


VMCHECKER_INI = 'vmchecker.ini'
VMCHECKER_DB = 'vmchecker.db'
DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

_config = None


def vmchecker_root():
    assert 'VMCHECKER_ROOT' in os.environ, (
        'VMCHECKER_ROOT environment variable not defined')
    return os.path.abspath(os.environ['VMCHECKER_ROOT'])


def config_file():
    """Returns absolute path for config file 'VMCHECKER_INI'"""
    path = os.path.join(vmchecker_root(), VMCHECKER_INI)
    assert os.path.isfile(path), '%s (%s) is not a file' % (
        VMCHECKER_INI, path)
    return path


def config():
    """Returns a RawConfigParse containing vmchecker's configuration."""
    global _config
    if _config is None:
        _config = ConfigParser.RawConfigParser()
        with open(config_file()) as handle:
            _config.readfp(handle)
    return _config



def relative_path(*args):
    """Joins the arguments and returns a path relative to root"""
    return os.path.join(vmchecker_root(), os.path.join(*args))


def repository(assignment):
    """Returns repository where sources for assignment are stored.
 
    NOTE: Full path where they are actually stored is
    `repository/assignment'"""
    return relative_path(config().get(assignment, 'Repository'))


def get_ip_address(ifname):
    """Returns ip address for network interface 'ifname'
    in standard dotted notation.

    Source from:
        http://code.activestate.com/recipes/439094/"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])


def db_file():
    """ The name of the DataBase file 
    @return
        - absolute path of config file
        - None if the path isn't a file"""

    path = os.path.join(vmchecker_root(), VMCHECKER_DB)
    if os.path.isfile(path):
        return path
    else:
        return None

