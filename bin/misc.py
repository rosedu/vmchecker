#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-
# vim: set expandtab :
from __future__ import with_statement

__author__ = 'Alexandru Mosoi <brtzsnr@gmail.com>'


import fcntl
import os
import socket
import struct

import ConfigParser


DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

_config = None



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
    return os.path.join(VmcheckerPaths().root, os.path.join(*args))


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

#todo
def db_file():
    """ The name of the DataBase file 
    @return
        - absolute path of config file
        - None if the path isn't a file"""
    path = VmcheckerPaths().db_file
    if os.path.isfile(path):
        return path
    else:
        return None


class VmcheckerPaths(object):
    """ All paths related to vmchecker. """
    def __init__(self):
        pass

    def abs_path(self, relative):
        return os.path.join(self.root, relative)

    @property
    def root(self):
        assert 'VMCHECKER_ROOT' in os.environ, (
            'VMCHECKER_ROOT environment variable not defined')
        return os.path.abspath(os.environ['VMCHECKER_ROOT'])

    @property
    def tester_paths(self):
        """ A list of all the paths relevant to the tester machine."""
        return [self.dir_queue]

    @property
    def storer_paths(self):
        """ A list of all the paths relevant to the storer machine."""
        return [self.dir_unchecked, self.dir_checked,
                self.dir_backup, self.dir_tests]

    @property
    def dir_unchecked(self):
        """ The absolute path of the unchecked homeworks
        are kept.
        This path is valid on the storer machine."""
        return self.abs_path("unchecked")

    @property
    def dir_checked(self):
        """ The absolute path of the checked homeworks
        are kept.
        This path is valid on the storer machine."""
        return self.abs_path("checked")

    @property
    def dir_tests(self):
        """ The absolute path of the test archives for the
        homeworks are kept.
        This path is valid on the storer machine."""
        return self.abs_path("tests")

    @property
    def dir_queue(self):
        """ The absolute path of the task queue directory.
        This path is valid on the tester machine."""
        return self.abs_path("queue")

    @property
    def dir_backup(self):
        """ The absolute path of the directory where backups
        of tasks are kept.
        This path is valid on the storer machine."""
        return self.abs_path("back")

    @property
    def db_file(self):
        """ The absolute path of the database file """
        return self.abs_path("vmchecker.db")

    @property
    def config_file(self):
        """Returns absolute path for config file 'VMCHECKER_INI'"""
        VMCHECKER_INI = 'vmchecker.ini'
        path = self.abs_path(VMCHECKER_INI)
        assert os.path.isfile(path), '%s (%s) is not a file' % (
            VMCHECKER_INI, path)
        return path
