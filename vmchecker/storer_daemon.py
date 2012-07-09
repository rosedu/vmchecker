#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Storer daemon

"""

from __future__ import with_statement

import os
import sys
import time
import shutil
import signal
import tempfile
import optparse
import subprocess

import xmlrpclib

from vmchecker.courselist import CourseList
from vmchecker.config import CourseConfig
from vmchecker.paths  import VmcheckerPaths
from vmchecker import vmlogging
from vmchecker import callback
from vmchecker import ziputil

from threading import Thread

import ConfigParser
import os
import shutil
import subprocess
import time
import socket
import random
import datetime

from vmchecker import config
from vmchecker import paths
from vmchecker import submissions
from vmchecker import tempfileutil

import warnings
with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	import paramiko # ignore deprecation warnings

from contextlib import closing
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

# The maximum number of seconds each instance of vmchecker-vm-executor
# is allowed to run. If it runs for more than this ammount of time,
# the process gets killed automatically by the queue manager
VMCHECKER_VM_EXECUTOR_MAXIMUM_RUNTIME = 10 * 60 # 10 minutes!

EXIT_SUCCESS = 0
EXIT_FAIL = 1


logger = vmlogging.create_module_logger('submit')

_DEFAULT_SSH_PORT = 22
_DEFAULT_KEY_PATH = '/home/sender/.ssh/id_rsa'

def ssh_bundle(bundle_path, vmcfg, assignment):
    """Sends a bundle over ssh to the tester machine"""
    machine = vmcfg.assignments().get(assignment, 'Machine')
    tester = vmcfg.get(machine, 'Tester')

    tstcfg = vmcfg.testers()

    tester_username  = tstcfg.login_username(tester)
    tester_hostname  = tstcfg.hostname(tester)
    tester_queuepath = tstcfg.queue_path(tester)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((tester_hostname, _DEFAULT_SSH_PORT))
    t = paramiko.Transport(sock)
    try:
        t.start_client()
        key = paramiko.RSAKey.from_private_key_file(_DEFAULT_KEY_PATH)
        t.auth_publickey(tester_username, key)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(bundle_path, os.path.join(tester_queuepath, os.path.basename(bundle_path)))
        
        myip = socket.gethostbyname(tester_hostname)
        server.register_function(notify, IP=myip)
    finally:
        t.close()
        
        
submission_path = {}
submission_index = 1

def create_testing_bundle(user, assignment, course_id):
    global submission_path, submission_index
    """Creates a testing bundle.

    This function creates a zip archive (the bundle) with everything
    needed to run the tests on a submission.

    The bundle contains:
        submission-config - submission config (eg. name, time of submission etc)
        course-config     - the whole configuration of the course
        archive.zip - a zip containing the sources
        tests.zip   - a zip containing the tests
        ???         - assignment's extra files (see Assignments.include())

    """
    vmcfg = config.CourseConfig(CourseList().course_config(course_id))
    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    sbroot = vmpaths.dir_cur_submission_root(assignment, user)

    asscfg  = vmcfg.assignments()
    machine = asscfg.get(assignment, 'Machine')
    
    fname = '/tmp/'+user
    index_file=open(fname, 'w')
    index_file.write("%d" % submission_index)
    index_file.close()
    
    submission_path[submission_index] = paths.submission_config_file(sbroot)
    submission_index += 1
    rel_file_list = [ ('run.sh',   vmcfg.get(machine, 'RunScript',   '')),
                      ('build.sh', vmcfg.get(machine, 'BuildScript', '')),
                      ('tests.zip', vmcfg.assignments().tests_path(vmpaths, assignment)),
                      ('course-config', vmpaths.config_file()),
                      ('submission-config', paths.submission_config_file(sbroot)),
                      ('submission-index', fname) ]

    # Get the assignment submission type (zip archive vs. MD5 Sum).
    # Large assignments do not have any archive.zip configured.
    if asscfg.getd(assignment, "AssignmentStorage", "").lower() != "large":
        rel_file_list += [ ('archive.zip', paths.submission_archive_file(sbroot)) ]


    file_list = [ (dst, vmpaths.abspath(src)) for (dst, src) in rel_file_list if src != '' ]

    # builds archive with configuration
    with vmcfg.assignments().lock(vmpaths, assignment):
        # creates the zip archive with an unique name
        (bundle_fd, bundle_path) = tempfileutil.mkstemp(
            suffix='.zip',
            prefix='%s_%s_%s_' % (course_id, assignment, user),
            dir=vmpaths.dir_storer_tmp())
        logger.info('Creating bundle package %s', bundle_path)

        try:
            with closing(os.fdopen(bundle_fd, 'w+b')) as handler:
                ziputil.create_zip(handler, file_list)
        except:
            logger.error('Failed to create zip archive %s', bundle_path)
            raise # just cleaned up the bundle. the error still needs
                  # to be reported.

    return bundle_path


def __queue_for_testing(assignment, user, course_id):
    """Queue for testing the last submittion for the given assignment,
    course and user."""
    vmcfg = config.CourseConfig(CourseList().course_config(course_id))
    bundle_path = create_testing_bundle(user, assignment, course_id)
    ssh_bundle(bundle_path, vmcfg, assignment)
    os.remove(bundle_path)
    print "done sending"
    print submission_path

def queue_for_testing(assignment, user, course_id):
    #t = Thread(target = __queue_for_testing, args=(assignment, user, course_id))
    #t.start()
    #print "called queue"
    __queue_for_testing(assignment, user, course_id)
    

submitted = {}
est_time = {}
# 'key':{'IP':'127.0.0.1', 'user':'so', 'bundle_path':'...'}    


def receive_files(IP, user, bundle_path, files):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, _DEFAULT_SSH_PORT))
    t = paramiko.Transport(sock)
    try:
        t.start_client()
        key = paramiko.RSAKey.from_private_key_file(LOCAL_KEY_PATH)
        t.auth_publickey(user, key)
        sftp = paramiko.SFTPClient.from_transport(t)
        for filepath in files:
            sftp.get(filepath, bundle_path+os.path.basename(filepath))
    finally:
        t.close()
    
    
def notify(key, status, files, stats):
    if key in submitted:
        info = submitted[key]
        del submitted[key]
        if status==0:
            # receive results
            receive_files(info['IP'], info['user'], info['bundle_path'], files) 
            # update stats
            ( et1, no1) = est_time[ (info['user'],info['IP']) ][info['assignment_id']]
            et2 = et1*no1 + stats['time']
            et2 = et2/(no1+1)
            est_time[ (info['user'],info['IP']) ][info['assignment_id']] = (et2, no1+1)       
        else: # apply a time penalty if the testing fails
            ( et1, no1) = est_time[ (info['user'],info['IP']) ]
            et2 = et1*no1 + TIME_PENALTY
            est_time[ (info['user'],info['IP']) ] = (et2, no1)
    else:
        logger.INFO('The key [%s] was not found. \n Details: %s %s %s' % (key,status,files,stats))


class SelectiveHandler(SimpleXMLRPCRequestHandler):
    def _dispatch(self, method, params):
        clientIP, clientPORT = self.client_address
        if method in self.server.restricted_functions:
            if not clientIP in self.server.restricted_functions[method]:
                raise Exception('Method "%s" cannot be called from %s' %(method,clientIP))
        func = None
        try:
            func = self.server.funcs[method]
        except KeyError:
            raise Exception('method "%s" is not supported' % method)
        if func is not None:
                return func(*params)
        else:
            raise Exception('method "%s" is not supported' % method)            
        
class SelectiveServer(SimpleXMLRPCServer):
    # restricted_functions = { "function_name":[ "IP1", "IP2" ] }
    # for the function_names in the hash, only the selected IP's are allowed
    restricted_functions = {}
    def register_function(self, function, name = None, IP = None):
        if not IP is None:
            if name is None:
                name = function.__name__
            if name in self.restricted_functions:
                if not IP in self.restricted_functions[name]:
                    self.restricted_functions[name].append(IP)
                    print "IP %s is allowed to call function %s" % (IP,name)
            else:    
                self.restricted_functions[name] = [ IP ]
                print "IP %s is allowed to call function %s" % (IP,name)
        SimpleXMLRPCServer.register_function(self,function, name)

def redirect_std_files(stdin_fname=None, stdout_fname=None, stderr_fname=None):
    """Redirect standard files for the files that are not null"""
    if stdin_fname != None:
        stdin = file(stdin_fname, 'r')
        os.dup2(stdin.fileno(), sys.stdin.fileno())

    if stdout_fname != None:
        sys.stdout.flush()
        stdout = file(stdout_fname, 'a+')
        os.dup2(stdout.fileno(), sys.stdout.fileno())

    if stderr_fname != None:
        sys.stderr.flush()
        stderr = file(stderr_fname, 'a+', 0)
        os.dup2(stderr.fileno(), sys.stderr.fileno())

server = None
        
def main():
    global server
    cmdline = optparse.OptionParser()
    cmdline.add_option('-0', '--stdin',  dest='stdin',  default=None,
                       help='Redirect stdin to FILE.',  metavar='FILE')
    cmdline.add_option('-1', '--stdout', dest='stdout', default=None,
                       help='Redirect stdout to FILE.', metavar='FILE')
    cmdline.add_option('-2', '--stderr', dest='stderr', default=None,
                       help='Redirect stderr to FILE.', metavar='FILE')
                       
    (options, _) = cmdline.parse_args()
    redirect_std_files(options.stdin, options.stdout, options.stderr)
    
    server = SelectiveServer(("", 19999), SelectiveHandler, allow_none=True)
    server.register_function(queue_for_testing, IP='127.0.0.1')
    server.register_function(notify, IP='dummyIP') # so the function is restricted
    server.serve_forever()
    
if __name__ == '__main__':
    main()
