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

STATUS_SAVED = 'saved'
STATUS_ERROR = 'error'
STATUS_QUEUED = 'queued'
STATUS_PROCESSING = 'running'
STATUS_DONE = 'done'

_logger = logging.getLogger('vmchecker.submissions')

def get_time_struct_from_str(time_str):
    """Returns a time_struct object from the time_str string given"""
    time_struct = time.strptime(time_str, DATE_FORMAT)
    return time_struct


def get_datetime_from_time_struct(time_struct):
    """Returns a datetime object from time time_struct given"""
    return datetime.datetime(*time_struct[:6])



class Submissions:
    """A class to manipulate submissions from a given repository"""
    def __init__(self, vmpaths):
        """Create a Submissions class.  vmpaths is a
        vmchecker.paths.VmcheckerPaths object holding information
        about one course configuration."""
        self.vmpaths = vmpaths


    def _get_submission_config_fname(self, assignment, account):
        """Returns the last submissions's configuration file name for
        the given account for the given assignment.

        If the config file cannot be found, returns None.
        """

        sbroot = self.vmpaths.dir_cur_submission_root(assignment, account)
        if not os.path.isdir(sbroot):
            return None

        config_file = paths.submission_config_file(sbroot)
        if not os.path.isfile(config_file):
            _logger.warn('%s found, but config (%s) is missing',
                         sbroot, config_file)
            return None
        return config_file



    def _get_submission_config(self, assignment, account):
        """Returns a ConfigParser for the last submissions's
        configuration file name for the given account for the given
        assignment.

        If the config file cannot be found, returns None.
        """
        config_file = self._get_submission_config_fname(assignment, account)
        if config_file == None:
            return None
        hrc = ConfigParser.RawConfigParser()
        with open(config_file) as handler:
            hrc.readfp(handler)
        return hrc


    def get_upload_time_str(self, assignment, account):
        """Returns a string representing the account's last submission date"""
        hrc = self._get_submission_config(assignment, account)
        if hrc == None:
            return None
        return hrc.get('Assignment', 'UploadTime')


    def get_eval_queueing_time_str(self, assignment, account):
        """Returns a string representing the last time the submission
        was queued for evaluation"""
        hrc = self._get_submission_config(assignment, account)
        if hrc == None:
            return None

        if not hrc.has_option('Assignment', 'EvaluationQueueingTime'):
            return None

        return hrc.get('Assignment', 'EvaluationQueueingTime')


    def get_upload_time_struct(self, assignment, account):
        """Returns a time_struct object with the upload time of the
        account's last submission"""
        upload_time_str = self.get_upload_time_str(assignment, account)
        return get_time_struct_from_str(upload_time_str)


    def get_upload_time(self, assignment, account):
        """Returns a datetime object with the upload time of the
        account's last submission"""
        upload_time_struct = self.get_upload_time_struct(assignment, account)
        return get_datetime_from_time_struct(upload_time_struct)


    def get_eval_queueing_time_struct(self, assignment, account):
        """Returns a time_struct object with the upload time of the
        last evaluation queueing for the user's last submission"""
        time_str = self.get_eval_queueing_time_str(assignment, account)
        return get_time_struct_from_str(time_str)


    def get_eval_queueing_time(self, assignment, account):
        """Returns a datetime object with the upload time of the last
        evaluation queueing for the account's last submission"""
        time_struct = self.get_eval_queueing_time_struct(assignment, account)
        return get_datetime_from_time_struct(time_struct)


    def set_eval_parameters(self, assignment, account, archive, eval_time):
        """Appends the archive filename to an existing
        submission-config (used for Large type assignments)"""
        config_file = self._get_submission_config_fname(assignment, account)
        if config_file == None:
            return None
        hrc = ConfigParser.RawConfigParser()
        with open(config_file) as handler:
            hrc.readfp(handler)

        hrc.set('Assignment', 'ArchiveFilename', archive)
        hrc.set('Assignment', 'EvaluationQueueingTime', eval_time)
        with open(config_file, "w") as handler:
            hrc.write(handler)

    def get_submitting_user(self, assignment, account):
        """In case the account is a mutual team account, return
           the name of the user that made the submission."""
        hrc = self._get_submission_config(assignment, account)
        if hrc == None:
            return None
        if not hrc.has_option('Assignment', 'SubmittingUser'):
            return None
        return hrc.get('Assignment', 'SubmittingUser')

    def get_tester(self, assignment, account):
        """Get the name of the tester used for the evaluation of
        this submission."""
        hrc = self._get_submission_config(assignment, account)
        if hrc == None:
            return None
        return hrc.get('Assignment', 'Tester')

    def set_tester(self, assignment, account, tester):
        """Appends the tester to an existing
        submission-config"""
        config_file = self._get_submission_config_fname(assignment, account)
        if config_file == None:
            return None
        hrc = ConfigParser.RawConfigParser()
        with open(config_file) as handler:
            hrc.readfp(handler)

        hrc.set('Assignment', 'Tester', tester)
        with open(config_file, "w") as handler:
            hrc.write(handler)

    def submission_exists(self, assignment, account):
        """Returns true if a valid submission exists for the given
        account and assignment"""
        return (self._get_submission_config(assignment, account) != None)

