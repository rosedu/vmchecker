#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A script that starts a vm, reverts it to a known snapshot, tests a
submission bundle (submission + tests), and closes the vm"""

from __future__ import with_statement


# Use simplejson or Python 2.6 json, prefer simplejson.
try:
    import simplejson as json
except ImportError:
    import json

import os
import sys
import time
import logging
import signal
import ConfigParser
from threading import Thread
from subprocess import Popen
import serial
from subprocess import Popen, PIPE, STDOUT
from vmchecker.config import VmwareMachineConfig, CourseConfig, VmwareConfig
from vmchecker.generic_executor import VM, Host
_logger = logging.getLogger('vm_executor')

class kvmHost(Host):
    def getVM(self, bundle_dir, vmcfg, assignment):
        return kvmVM(self, bundle_dir, vmcfg, assignment)

class kvmVM(VM):
    hostname = 'kvm2'
    def __init__(self, host, bundle_dir, vmcfg, assignment):
        VM.__init__(self, host, bundle_dir, vmcfg, assignment)
        self.hostname = self.machinecfg.get_vmx_path()
        self.path = self.getPath()
        print self.path
        
    def executeCommand(self,cmd):
        _logger.info("executeCommand: %s" % cmd)
        return self.host.executeCommand("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+self.username+"@"+self.IP+" "+cmd)

    def power_on_kvm(self):
	    o = self.host.executeCommand("virsh start kvm2")
	    if "started" in o:
		    print "Exit"
		    sys.exit()

    def start(self):
        power_thd = Thread(target = self.power_on_kvm)
        power_thd.start()
        power_thd.join()
        self.IP = self.getIP()
    
    def stop(self):
        self.host.executeCommand("virsh destroy "+self.hostname)
            
    def revert(self, number = None):
        self.stop() # just in case it's on
        self.host.executeCommand("rm -f "+os.path.join(self.path,"run.qcow2"))
        self.host.executeCommand("cp "+os.path.join(self.path,"image.qcow2")+" "+os.path.join(self.path,"run.qcow2"))
        
       
    def copyTo(self, sourceDir, targetDir, files):
        """ Copy files from host(source) to guest(target) """
        for f in files:
            host_path = os.path.join(sourceDir, f)
            guest_path = os.path.join(targetDir, f)
            if not os.path.exists(host_path):
                _logger.error('host file (to send) "%s" does not exist' % host_path)
                return
            _logger.info('copy file %s from host to guest at %s' % (host_path, guest_path))
            self.host.executeCommand("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  -r "+host_path+" "+self.username+"@"+self.IP+":"+guest_path)
        
    def copyFrom(self, sourceDir, targetDir, files):
        """ Copy files from guest(source) to host(target) """
        for f in files:
            host_path = os.path.join(targetDir, f)
            guest_path = os.path.join(sourceDir, f)
            _logger.info('copy file %s from guest to host at %s' % (guest_path, host_path))
            self.host.executeCommand("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  -r "+self.username+"@"+self.IP+":"+guest_path+" "+host_path)
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

    def getMac(self):
        mac = self.host.executeCommand("virsh dumpxml "+self.hostname)
        mac = mac[mac.find("<mac address=")+14:]
        mac = mac[:mac.find("'/>")]
        return mac.strip()

    def getPath(self):
        path = self.host.executeCommand("virsh dumpxml "+self.hostname)
        path = path[path.find("<source file='")+14:]
        path = path[:path.find("'/>")]
        return os.path.dirname(path)
	    
    def getIP(self):
        mac = self.getMac()
        while True:
            arps = self.host.executeCommand("arp -a").split("\n")
            time.sleep(1)
            for arp in arps:
                if mac in arp:
                    IP = arp[arp.find("(")+1:arp.find(")")]
                    _logger.info("IP: %s" % IP)
                    return IP
        
    
    def getIPfromIfconfig(self,string):
	    s = string[string.find("inet addr:")+10:]
	    s = s[0:s.find(" ")]
	    return s


