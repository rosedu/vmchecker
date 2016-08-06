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
DEFAULT_LDAP_CONFIG = './etc/vmchecker/ldap.config'
DEFAULT_ACL_CONFIG = './etc/vmchecker/acl.config'


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

    def revert_to_snapshot(self, assignment):
        """Should the machine be reverted to it's last snapshot?"""
        val = self.getd(assignment, 'RevertToSnapshot', 'yes')
        val = val.strip().lower()
        return (val == 'yes') or (val == 'y') or (val == 'true')


    def delay_between_tools_and_tests(self, assignment):
        """After Vmware tools are loaded, there may be some time
        before the machine is actually usable (services like apache,
        mysql, et al. must be started). This defines an amount of time
        (in seconds) to wait after tools are up, but before starting
        to run the tests.

        If the config file does not set DelayBetweenToolsAndTests it
        defaults to 0.

        """
        val = self.getd(assignment, 'DelayBetweenToolsAndTests', '0')
        return int(val)


    def delay_wait_for_tools(self, assignment):
        """How much time (in seconds) to wait for vmware tools to load."""
        tools_timeout = self.getd(assignment, 'WaitForVmwareToolsTimeout', None)
        if tools_timeout == None:
            return None
        return int(tools_timeout)

    def storage_basepath(self, assignment, username):
        """When using an external storage server (for Large assignments).
           the basepath can be particularized depending on its configuration.
           Because of this there can be special expressions inserted in the path
           to help overcome this. We use the format expression to handle this.
           So far we only support username variations inserted.
           
           The syntax is that supported by format.
           
           Example:
                /home/{username[0]}/files for username = john.doe
                would translate to:
                /home/j/files
        """
        basepath = self.get(assignment, 'AssignmentStorageBasepath')
        try:
            result = basepath.format(username = username)
        except:
            # This is crude, yes, I know, but not every one has python2.6
            while not basepath.find('{') == -1:
                st_idx = basepath.find('{')
                fin_idx = basepath.find('}')
                token = basepath[st_idx + 1:fin_idx]
                basepath = basepath[:st_idx] + eval(token) + basepath[fin_idx+1:]
            result = basepath

        return result

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




class VmwareConfig():
    """Configuration for the VMWare solution used for testing
    (Server or Workstation)"""

    def __init__(self, tstcfg, tester_id):
        self.tstcfg = tstcfg
        self.tester_id = tester_id


    def vmware_register_and_unregister(self):
        """Should the vmx be unregistered at shutdown?"""
        if not self.tstcfg.has(self.tester_id, 'VmwareRegUnreg'):
            return False # if key not present, don't reg/unreg

        val = self.tstcfg.get(self.tester_id, 'VmwareRegUnreg')
        val = val.strip().lower()
        return val == "1" or val == "yes" or val == "y" or val == "true"


    def vmware_type(self):
        """The type of the VMWare server encoded as an int for pyvix.Host()"""
        type_str = self.tstcfg.get(self.tester_id, 'VmType').lower()
        if type_str == "vmwareserver":
            return 2 # VIX_SERVICEPROVIDER_VMWARE_SERVER
        elif type_str == "vmwareworkstation":
            return 3 # VIX_SERVICEPROVIDER_VMWARE_WORKSTATION
        elif type_str == "vmwareviserver":
            return 10 # VIX_SERVICEPROVIDER_VMWARE_VI_SERVER
        else:
            return 1 # VIX_SERVICEPROVIDER_DEFAULT


    def vmware_url(self):
        """The URL of the VMWare server"""
        return self.tstcfg.get(self.tester_id, 'VmwareUrl')


    def vmware_hostname(self):
        """The hostname of the VMWare server"""
        return self.tstcfg.get(self.tester_id, 'VmwareHostname')


    def vmware_port(self):
        """The port of the VMWare Server"""
        return self.tstcfg.get(self.tester_id, 'VmwarePort')


    def vmware_username(self):
        """The username used to access the VMWare Server"""
        return self.tstcfg.get(self.tester_id, 'VmwareUsername')


    def vmware_password(self):
        """The password used to access the VMWare Server"""
        return self.tstcfg.get(self.tester_id, 'VmwarePassword')


    def vmware_datastore_name(self):
        """The VMWare Server datastore name containing the path to the
        machines"""
        return self.tstcfg.get(self.tester_id, 'VmwareDatastoreName')


    def vmware_datastore_path(self):
        """The VMWare Server datastore path with the above name"""
        return self.tstcfg.get(self.tester_id, 'VmwareDatastorePath')


    def vmware_rel_vmx_path(self, vmx_path):
        """The path given to register/unregister/powerOn operations
           has to be relative to the datastore in VMWare Server 2.0."""
        datastore_name = self.vmware_datastore_name()
        datastore_path = self.vmware_datastore_path()
        rel_vmx_path = vmx_path[len(datastore_path):].lstrip('/')
        return "[" + datastore_name + "] " + rel_vmx_path



class VmwareMachineConfig(object):
    """Configuration for a virtual machine:
       * how to login
       * where to store files
       * which is the shell
    """


    def __init__(self, config, machine_id):
        self.config = config
        self.machine_id = machine_id


    def get_tester_id(self):
        """Returns the id of a tester configuration.

        The config script contains sections named
            [tester TESTER_ID]
        from which more info about the tester can be determined.
        """
        return self.config.get(self.machine_id, 'Tester')


    def get_vmx_path(self):
        """Path to a .vmx file to be used"""
        path = self.config.get(self.machine_id, 'VMPath', '')
        if path == '':
            return None
        return path


    def guest_user(self):
        """The user (from the guest virtual machine) used to authenticate"""
        return self.config.get(self.machine_id, 'GuestUser')


    def guest_pass(self):
        """The password (from the guest virtual machine) used to authenticate"""
        return self.config.get(self.machine_id, 'GuestPassword')


    def guest_base_path(self):
        """The path where the test+homework files will be stored in
        the virtual machine.

        This path is written in the way the guest operating system
        demands it.

        E.g.:
        - in Linux: /home/test/
        - in Windows (cygwin): C:\cygwin\home\Administrator
        - in Windows (native): C:\Users\Administrator
        """
        return self.config.get(self.machine_id, 'GuestBasePath')


    def guest_shell_path(self):
        """The path to the shell inside the virtual machine invoked to
        run the build and run script files.

        This path is written in the way the guest operating system
        demands it.

        E.g.:
        - in Linux: /bin/bash
        - in Windows (cygwin): C:\cygwin\bin\bash.exe
        - in Windows (native): C:\windows\cmd.exe
        """
        return self.config.get(self.machine_id, 'GuestShellPath')


    def guest_home_in_shell(self):
        """The same path as returned by guest_base_path(), but written
        in the way expected by the shell.

        This path is written in the way the guest operating system
        demands it.

        E.g.:
        - in Linux: /home/test
        - in Windows (cygwin): /home/Administrator
        - in Windows (native): C:\Users\Administrator
        """
        return self.config.get(self.machine_id, 'GuestHomeInBash')


    def guest_build_script(self):
        """The name of the script used to build the homework and tests"""
        return self.config.get(self.machine_id, 'BuildScript')


    def guest_run_script(self):
        """The name of the script used to run the homework and tests"""
        return self.config.get(self.machine_id, 'RunScript')
