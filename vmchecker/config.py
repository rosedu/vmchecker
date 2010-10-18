#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General configuration module"""


from __future__ import with_statement

import os
import time
import datetime
import ConfigParser

from . import dirlocking
from . import confdefaults


DATE_FORMAT = '%Y.%m.%d %H:%M:%S'
DEFAULT_LDAP_CONFIG = '/etc/vmchecker/ldap.config'
DEFAULT_ACL_CONFIG = '/etc/vmchecker/acl.config'


class CourseConfig:
    """An object that encapsulates parsing of the config file of a course"""
    def __init__(self, config_file_):
        self.config_file = config_file_
        self.config = ConfigParser.RawConfigParser()
        with open(os.path.expanduser(config_file_)) as handle:
            self.config.readfp(handle)

    def get(self, section, option, default=None):
        """A convenient wrapper for config.get()"""
        if default != None and not self.config.has_option(section, option):
            return default
        return self.config.get(section, option)


    def repository_path(self):
        """Get the submission (git) repository path for this course."""
        return self.config.get('vmchecker', 'repository')

    def sections(self):
        """Give access to the underlining config's sections"""
        # XXX: LAG: I think this is a sign that we should have derived the
        # RawConfigParser class.
        return self.config.sections()

    def root_path(self):
        """Get the root path for this course"""
        return self.config.get('vmchecker', 'root')

    def storer_username(self):
        """The username to use when logging in with ssh to the storer machine"""
        return self.config.get('storer', 'username')

    def storer_hostname(self):
        """The hostname to use when logging in with ssh to the storer machine"""
        return self.config.get('storer', 'hostname')

    def storer_sshid(self):
        """The ssh id used to communicate from the storer to the testers"""
        return self.config.get('storer', 'sshid')

    def known_hosts_file(self):
        """The path on the storer machine where the known_hosts file to
        use to connect to testers is located."""
        return self.get('storer', 'KnownHostsFile')

    def course_name(self):
        """Return a human readable name for the course"""
        return self.config.get('vmchecker', 'coursename')

    def upload_active_interval(self):
        """Time interval when upload is active.

        Return a tuple of time.struct_time objects describing the
        period in which howework upload is active in vmchecker for
        this course.
        """
        start = self.config.get('vmchecker', 'UploadActiveFrom')
        stop  = self.config.get('vmchecker', 'UploadActiveUntil')
        return (time.strptime(start, DATE_FORMAT),
                time.strptime(stop, DATE_FORMAT))

    def assignments(self):
        """Return an AssignmentsConfig object describing the
        assignments in this course's config file"""
        return AssignmentsConfig(self)

    def testers(self):
        """Return an TestersConfig object describing the
        tester machines used."""
        return TestersConfig(self)



class LdapConfig():
    """Info for interaction with LDAP for student/teaching
    assistent authentication"""
    def __init__(self, ldap_cfg_fname=DEFAULT_LDAP_CONFIG):
        self.config = ConfigParser.RawConfigParser()
        with open(os.path.expanduser(ldap_cfg_fname)) as handle:
            self.config.readfp(handle)
    def server(self):
        """Get LDAP server"""
        return self.config.get('DEFAULT', 'LDAP_SERVER')

    def bind_user(self):
        """Get LDAP bind user"""
        return self.config.get('DEFAULT', 'LDAP_BIND_USER')

    def bind_pass(self):
        """Get LDAP bind pass"""
        return self.config.get('DEFAULT', 'LDAP_BIND_PASS')

    def root_search(self):
        """Get LDAP root search"""
        return self.config.get('DEFAULT', 'LDAP_ROOT_SEARCH')



class AclConfig():
    """Configuration for the users and groups that will implicitly
    receive default ACLs for all storer root folders"""
    def __init__(self, acl_cfg_fname=DEFAULT_ACL_CONFIG):
        self.config = ConfigParser.RawConfigParser()
        with open(acl_cfg_fname) as handle:
            self.config.readfp(handle)

    def users(self):
        """The list of users that will receive default ACLs"""
        return self.config.get('DEFAULT', 'users').split(' ')

    def groups(self):
        """The list of groups that will receive default ACLs"""
        return self.config.get('DEFAULT', 'groups').split(' ')



class AssignmentsConfig(confdefaults.ConfigWithDefaults):
    """Obtain information about assignments from a config file.

        [assignment DEFAULT]
        somevar = somveval

        [assignment as1]
        somevar = somveval

        [assignment as2]
        somevar = somveval
    """

    def __init__(self, config):
        confdefaults.ConfigWithDefaults.__init__(self, config, 'assignment ')


    def lock(self, vmpaths, assignment):
        """Returns a lock over assignment"""
        self._check_valid(assignment)
        return dirlocking.DirLock(vmpaths.dir_assignment(assignment))


    def course(self, assignment):
        """Returns a string representing course name of assignment"""
        return self.get(assignment, 'course')


    def tests_path(self, vmpaths, assignment):
        """Returns the path to the tests for assignment"""
        self._check_valid(assignment)
        return os.path.join(vmpaths.dir_tests(), assignment + '.zip')


    def timedelta(self, assignment):
        """Returns a timedelta object with minimum delay between submissions"""
        return datetime.timedelta(seconds=int(
                self.get(assignment, 'timedelta')))



class TestersConfig(confdefaults.ConfigWithDefaults):
    """Obtain information about assignments from a config file.

        [tester DEFAULT]
        somevar = somveval

        [tester as1]
        somevar = somveval

        [tester as2]
        somevar = somveval
    """

    def __init__(self, config):
        confdefaults.ConfigWithDefaults.__init__(self, config, 'tester ')


    def login_username(self, tester):
        """The username to use when logging in with ssh to the tester machine"""
        return self.get(tester, 'username')


    def hostname(self, tester):
        """The hostname to use when logging in with ssh to the tester machine"""
        return self.get(tester, 'hostname')


    def queue_path(self, tester):
        """The path on the tester machine where the queued files are put"""
        return self.get(tester, 'queuepath')
