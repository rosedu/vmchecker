#!/usr/bin/env python
# Open Nebula executor
# Lucian Cojocar <cojocar@rosedu.org>

import logging
import os
import paramiko
import socket
import time
import xmlrpclib

from xml.dom import minidom

from vmchecker.config import OneMachineConfig
from vmchecker.generic_executor import Host, VM

_logger = logging.getLogger('vm_executor')

class OneHost(Host):
    def getVM(self, bundle_dir, vmcfg, assignment):
        return OneVM(self, bundle_dir, vmcfg, assignment)

class OneVMException(Exception):
    pass

class OneVM(VM):
    # this module works with the assumtipon that there is a snapshot that we can use
    # start means resume to snapshot
    # stop means resume to snapshot
    # resume means resume (but) it should not be used from outside
    # start and stop operations are blocking (i.e. we wait for the machine to
    # be up again)
    def __init__(self, host, bundle_dir, vmcfg, assignment):
        VM.__init__(self, host, bundle_dir, vmcfg, assignment)
        self.machinecfg = OneMachineConfig(vmcfg, self.machine)
        self.one_server = self.machinecfg.get_one_server()
        self.one_credentials = self.machinecfg.get_one_credentials()

        self.vm_id = int(self.machinecfg.get_one_vm_id())
        self.one_vm_hostname = self.machinecfg.get_one_vm_hostname()
        self.vm_username = self.machinecfg.guest_user()
        self.snapshot_id = 0

        # we cannot use the revert mechanism from outside
        asscfg = vmcfg.assignments()
        assert(False == asscfg.revert_to_snapshot(assignment))

    def start(self):
        # assume that the vm has been already suspended in a good state
        _logger.info("starting vm %d" % self.vm_id)
        self.revert(self.snapshot_id)
        while not self.hasStarted():
            time.sleep(1)
            _logger.info("start wait for %d" % self.vm_id)

    def stop(self):
        # cleanup the work (do not suspend)
        _logger.info("stopping vm %d" % self.vm_id)
        self.revert(self.snapshot_id)
        while not self.hasStarted():
            time.sleep(1)
            _logger.info("stop wait for %d" % self.vm_id)

    def hasStarted(self):
        state, state_ext = self._get_state()
        if state == 3 and state_ext == 3:
            return True
        return False

    def executeCommand(self, cmd):
        _logger.debug("execute on vm %d: %s" % \
                (self.vm_id, cmd))

        client = self._create_ssh_connection()

        try:
            # this doesn't waits for the commands (I think)
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.close()
            stdout.close()
            stderr.close()
        finally:
            client.close()

    def revert(self, number = None):
        if not number:
            number = self.snapshot_id
        _logger.info("doing revert to snapshot id %d" % number)

        REVERT_TIMEOUT = 10
        cnt = 0
        while not self.hasStarted() and cnt < REVERT_TIMEOUT:
            cnt += 1
            time.sleep(1)
            _logger.info("revert wait for %d" % self.vm_id)

        if cnt == REVERT_TIMEOUT:
            _logger.warning("probably failing")

        self._rpc('one.vm.snapshotrevert', self.vm_id, number)

    def copyTo(self, sourceDir, targetDir, files):
        _logger.info("copy to vm %d, %s->%s (%s)" % \
                (self.vm_id, sourceDir, targetDir, files))

        t, sftp = self._create_sftp_connection_to_vm()
        try:
            for f in files:
                src_f = os.path.join(sourceDir, f)
                # assume remote path delim == host path delim
                dst_f = os.path.join(targetDir, f)
                sftp.put(src_f, dst_f, confirm=True)
        finally:
            t.close()

    def copyFrom(self, sourceDir, targetDir, files):
        _logger.info("copy from vm %d, %s->%s (%s)" % \
                (self.vm_id, sourceDir, targetDir, files))

        t, sftp = self._create_sftp_connection_to_vm()
        try:
            for f in files:
                src_f = os.path.join(sourceDir, f)
                # assume remote path delim == host path delim
                dst_f = os.path.join(targetDir, f)
                sftp.get(src_f, dst_f)
        finally:
            t.close()

    def run(self, shell, executable_file, timeout):
        _logger.info("run on vm %d: %s %s" % \
                (self.vm_id, shell, executable_file))

        cmd = shell+' '+executable_file+' '+str(timeout)

        client = self._create_ssh_connection()
        try:
            stdin, stdout, stderr = client.exec_command(cmd)

            while timeout > 0 and not stdout.channel.exit_status_ready():
                time.sleep(1)
                timeout -= 1
                _logger.debug('wait for cmd to finish: [%s]' % cmd)

            stdin.close()
            stdout.close()
            stderr.close()
        finally:
            client.close()

    def _create_ssh_connection(self):
        client = paramiko.SSHClient()
        try:
            # XXX: we should use a more strict policy
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.one_vm_hostname,
                    username=self.vm_username)
        except:
            client.close()
            raise
        return client

    def _create_sftp_connection_to_vm(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(self.one_vm_hostname)
        sock.connect((ip, 22))
        t = paramiko.Transport(sock)
        try:
            t.start_client()
            sftp = None

            key = paramiko.RSAKey.from_private_key_file(\
                        os.path.join(os.environ['HOME'], '.ssh/id_rsa'))
            t.auth_publickey(self.vm_username, key)
            sftp = paramiko.SFTPClient.from_transport(t)
        except:
            t.close()
            t = None
            sftp = None
            raise

        return (t, sftp)

    def _get_state(self):
          # http://docs.opennebula.org/4.4/integration/system_interfaces/api.html#one-vm-info
          # INIT      = 0
          # PENDING   = 1
          # HOLD      = 2
          # ACTIVE    = 3
          # STOPPED   = 4
          # SUSPENDED = 5
          # DONE      = 6
          # FAILED    = 7
          # POWEROFF  = 8
          # UNDEPLOYED = 9

          #LCM_INIT            = 0,
          #PROLOG              = 1,
          #BOOT                = 2,
          #RUNNING             = 3,
          #MIGRATE             = 4,
          #SAVE_STOP           = 5,
          #SAVE_SUSPEND        = 6,
          #SAVE_MIGRATE        = 7,
          #PROLOG_MIGRATE      = 8,
          #PROLOG_RESUME       = 9,
          #EPILOG_STOP         = 10,
          #EPILOG              = 11,
          #SHUTDOWN            = 12,
          #CANCEL              = 13,
          #FAILURE             = 14,
          #CLEANUP_RESUBMIT    = 15,
          #UNKNOWN             = 16,
          #HOTPLUG             = 17,
          #SHUTDOWN_POWEROFF   = 18,
          #BOOT_UNKNOWN        = 19,
          #BOOT_POWEROFF       = 20,
          #BOOT_SUSPENDED      = 21,
          #BOOT_STOPPED        = 22,
          #CLEANUP_DELETE      = 23,
          #HOTPLUG_SNAPSHOT    = 24,
          #HOTPLUG_NIC         = 25,
          #HOTPLUG_SAVEAS           = 26,
          #HOTPLUG_SAVEAS_POWEROFF  = 27,
          #HOTPLUG_SAVEAS_SUSPENDED = 28,
          #SHUTDOWN_UNDEPLOY   = 29,
          #EPILOG_UNDEPLOY     = 30,
          #PROLOG_UNDEPLOY     = 31,
          #BOOT_UNDEPLOY       = 32

        _, info, _ = self._rpc('one.vm.info', self.vm_id)
        xmldoc = minidom.parseString(info)
        state = int(xmldoc.getElementsByTagName('STATE')[0].firstChild.nodeValue)
        state_ext = int(xmldoc.getElementsByTagName('LCM_STATE')[0].firstChild.nodeValue)
        if state != 3:
            state_ext = None

        _logger.debug("state form vm %d is (%s:%s)" % (self.vm_id, state, state_ext))
        return (state, state_ext)

    def _get_proxy(self):
        return xmlrpclib.ServerProxy(self.one_server)

    def _rpc(self, *kargs):
        p = self._get_proxy()
        method = getattr(p, kargs[0])
        ret = method(self.one_credentials, *kargs[1:])
        #_logger.debug("%s" % str(ret))
        if not ret[0]:
            raise OneVMException("One RPC: %s" % ret[1])
        return ret

