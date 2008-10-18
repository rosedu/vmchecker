#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
# vim: set expandtab :


__author__ = 'Alexandru Mosoi, brtzsnr@gmail.com'


import fcntl
import os
import socket
import struct


VMCHECKER_INI = 'vmchecker.ini'
VMCHECKER_DB = 'vmchecker.db'


def vmchecker_root():
    assert 'VMCHECKER_ROOT' in os.environ, (
        'VMCHECKER_ROOT environment varible not defined')
    return os.path.abspath(os.environ['VMCHECKER_ROOT'])


def config_file():
    """Returns absolute path for config file 'VMCHECKER_INI'"""
    path = os.path.join(vmchecker_root(), VMCHECKER_INI)
    assert os.path.isfile(path), '%s (%s) is not a file' % (
        VMCHECKER_INI, path)
    return path


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

def get_option(config, homework, option, default=None):
    """Given homework name, returns option. If option not found
    in [homework] section, then option is looked up in [DEFAULT]
    section.  If there is no such option, returns default."""

    assert config.has_section(homework), 'No such homework %s' % homework

    # first tries to get option from `homework` section
    if config.has_option(homework, option):
        return config.get(homework, option)

    # falls back to default remote ip
    if config.has_option('DEFAULT', option):
        return config.get('DEFAULT', option)

    return default
