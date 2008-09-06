#! /usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set expandtab :


__author__ = 'Alexandru Mosoi, brtzsnr@gmail.com'


import os


def vmchecker_root():
    assert 'VMCHECKER_ROOT' in os.environ, (
        'VMCHECKER_ROOT environment varible not defined')
    return os.environ['VMCHECKER_ROOT']


def config_file():
    """Searches up on directory structure for file_name.
    @return
        - absolute path of config file
        - None, if file not found"""

    path = os.path.join(vmchecker_root(), 'vmchecker.ini')
    assert os.path.isfile(path), 'vmchecker.ini is not a file'
    return path


def get_option(config, homework, option):
    """Given homework name, returns option.
    If there is no such option, returns None."""

    assert config.has_section(homework), 'No such homework %s' % homework

    # first tries to get option from `homework` section
    if config.has_option(homework, option):
        return config.get(homework, option)

    # falls back to default remote ip
    if config.has_option('DEFAULT', option):
        return config.get('DEFAULT', default)
