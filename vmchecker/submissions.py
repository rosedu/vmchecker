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

from vmchecker.config import DATE_FORMAT
from vmchecker import paths

_logger = logging.getLogger('vmchecker.submissions')

class Submissions:
    def __init__(self, vmpaths):
        self.vmpaths = vmpaths

    def _get_submission_location(self, assignment, user):
        location = self.vmpaths.dir_submission_root(assignment, user)
        if not os.path.isdir(location):
            return None
        return location


    def _get_submission_config(self, assignment, user):
        location = self._get_submission_location(assignment, user)
        if location == None:
            return None

        config_file = paths.submission_config_file(location)
        if not os.path.isfile(config_file):
            _logger.warn('%s found, but config (%s) is missing',
                         location, config_file)
            return None
        return config_file


    def get_upload_time_str(self, assignment, user):
        """Returns a datetime object with upload time user's last submission"""
        config_file = self._get_submission_config(assignment, user)
        if config_file == None:
            return None
        hrc = ConfigParser.RawConfigParser()
        with open(config_file) as handler:
            hrc.readfp(handler)

        upload_time = hrc.get('Assignment', 'UploadTime')
        upload_time = time.strptime(upload_time, DATE_FORMAT)
        return upload_time

    def get_upload_time(self, assignment, user):
        return datetime.datetime(*self.get_upload_time_str(assignment, user)[:6])

    def submission_exists(self, assignment, user):
        return (self._get_submission_config(assignment, user) != None)

