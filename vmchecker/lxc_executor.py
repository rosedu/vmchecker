#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from vmchecker.generic_executor import Host,VM
_logger = logging.getLogger('vm_executor')
from threading import Thread


class LXCHost(Host):
    def getVM(self, bundle_dir, vmcfg, assignment):
        return LXCVM(self, bundle_dir, vmcfg, assignment)

class LXCVM(VM):
    hostname = 'deb1'
    #hostpath = '/var/lib/lxc/'+hostname
    def executeCommand(self,cmd):
        return self.host.executeCommand("ssh "+self.username+"@"+self.hostname+" "+cmd)
    
    def start(self):
        self.host.executeCommand("lxc-start -n "+self.hostname+" -d")
        while True:
            if self.hasStarted():
                return
    
    def stop(self):
        self.host.executeCommand("lxc-stop -n "+self.hostname)

    def hasStarted(self):
        o = self.host.executeCommand("lxc-info -n "+self.hostname)
        if "-1" in o:
            return False
        if "refused" in self.executeCommand('echo hello'):
            return False
        return True
            
    
    def revert(self, number = None):
        '''
        TODO:
        1. replace hardcoded paths with configurable options
        2. provide a way for starting multiple containters at the same time
        '''
        self.host.executeCommand("lxc-stop -n "+self.hostname)
        self.host.executeCommand("rm -rf /var/lib/lxc/"+self.hostname+"/rootfs")
        self.host.executeCommand("cp -pr /lxc/rootfs /var/lib/lxc/"+self.hostname)
        #self.start()
       
    def copyTo(self, sourceDir, targetDir, files):
        """ Copy files from host(source) to guest(target) """
        for f in files:
            host_path = os.path.join(sourceDir, f)
            guest_path = os.path.join(targetDir, f)
            guest_path = "/var/lib/lxc/"+self.hostname+"/rootfs"+guest_path
            if not os.path.exists(host_path):
                _logger.error('host file (to send) "%s" does not exist' % host_path)
                return
            _logger.info('copy file %s from host to guest at %s' % (host_path, guest_path))
            self.host.executeCommand("cp %s %s" % (host_path,guest_path))
        
    def copyFrom(self, sourceDir, targetDir, files):
        """ Copy files from guest(source) to host(target) """
        for f in files:
            host_path = os.path.join(targetDir, f)
            guest_path = os.path.join(sourceDir, f)
            guest_path = "/var/lib/lxc/"+self.hostname+"/rootfs"+guest_path
            _logger.info('copy file %s from guest to host at %s' % (guest_path, host_path))
            self.host.executeCommand("cp %s %s" % (guest_path,host_path))
            if not os.path.exists(host_path):
                _logger.error('host file (received) "%s" does not exist' % host_path)

    def run(self, shell, executable_file, timeout):
        self.executeCommand("chmod +x "+ executable_file)
        _logger.info('executing on the remote: prog=%s args=[%s] timeout=%d' % (shell, executable_file, timeout))
        thd = Thread(target = self.executeCommand, args = (executable_file,))
        thd.start()
        if timeout==None:
            thd.join()
        else:
            thd.join(timeout)
        return thd.isAlive()
        

    
