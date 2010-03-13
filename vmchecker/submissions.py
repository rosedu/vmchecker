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

from .config import DATE_FORMAT
from . import paths

_logger = logging.getLogger('vmchecker.submissions')

class Submissions:
    """A class to manipulate submissions from a given repository"""
    def __init__(self, vmpaths):
        """Create a Submissions class.  vmpaths is a
        vmchecker.paths.VmcheckerPaths object holding information
        about one course configuration."""
        self.vmpaths = vmpaths


    def _get_submission_config(self, assignment, user):
        """Returns the configuration file for the last submision of
        the given user for the given assignment.

        If the config file cannot be found, returns None.
        """

        sbroot = self.vmpaths.dir_submission_root(assignment, user)
        if not os.path.isdir(sbroot):
            return None

        config_file = paths.submission_config_file(sbroot)
        if not os.path.isfile(config_file):
            _logger.warn('%s found, but config (%s) is missing',
                         sbroot, config_file)
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
        """Returns true if a valid submission exists for the given
        user and assignment"""
        return (self._get_submission_config(assignment, user) != None)

