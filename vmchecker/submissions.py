#! /bin/bin/env python
# -*- coding: utf-8 -*-

"""


"""

from __future__ import with_statement

import ConfigParser
import os
import time
import datetime
import logging

import config
import vmcheckerpaths

_logger = logging.getLogger('submit')

def _get_submission_location(assignment, user):
    location = vmcheckerpaths.dir_user(assignment, user)
    if not os.path.isdir(location):
        return None
    return location


def _get_submission_config(assignment, user):
    location = _get_submission_location(assignment, user)
    if location == None:
        return None

    config_file = os.path.join(location, 'config')
    if not os.path.isfile(config_file):
        _logger.warn('%s found, but config (%s) is missing',
                     location, config_file)
        return None
    return config_file

def get_upload_time_str(assignment, user):
    """Returns a datetime object with upload time user's last submission"""
    config_file = _get_submission_config(assignment, user)
    if config_file == None:
        return None
    hrc = ConfigParser.RawConfigParser()
    with open(config_file) as handler:
        hrc.readfp(handler)

    upload_time = hrc.get('Assignment', 'UploadTime')
    upload_time = time.strptime(upload_time, config.DATE_FORMAT)
    return upload_time

def get_upload_time(assignment, user):
    return datetime.datetime(*get_upload_time_str(assignment, user)[:6])

def submission_exists(assignment, user):
    return (_get_submission_config(assignment, user) != None)

