#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Callback script executed on the tester machine
"""
from __future__ import with_statement

import base64
import getpass
import os
import socket
import traceback
import paramiko
import sys
import misc, vmcheckerpaths
import ConfigParser
import logging

_logger = logging.getLogger("vmchecker.callback")


def config_reader(config_path):
    """Returns a RawConfigParser for 'config'
    """
    config = ConfigParser.RawConfigParser()
    with open(config_path) as handle:
        config.readfp(handle)
    return config


def config_variables(config_path):
    """Return a dictionary with values from the config_path file.
    """
    conf_reader = config_reader(config_path)
    keys = ['User', 'Assignment', 'UploadTime', 'RepoPath',
            'RemoteHostname', 'RemoteUsername']
    section_name = 'Assignment'
    ret = {}
    for key in keys:
        val = conf_reader.get(section_name, key)
        ret[key] = val
    return ret


def _setup_logging():
    """Instruct paramiko to log stuff. Should be disabled in production?
    """
    paramiko.util.log_to_file('callback_sftp.log')


def get_default_host_keys():
    """Search for host keys in default paths
    """
    # search two default paths (Linux & Windows)
    default_search_paths = ['~/.ssh/known_hosts', '~/ssh/known_hosts']
    default_search_paths = map(lambda x : os.path.expanduser(x), default_search_paths)
    for path in default_search_paths:
        try:
            host_keys = paramiko.util.load_host_keys(path)
            return host_keys
        except:
            _logger.info('Cannot open known_hosts file [%s]' % path)
    else:
        # on failure return an empty key dictionary
        return {}


def is_remote_server_key_known(key, hostname):
    """Return True if the remote hostname server key is found in
    default known_hosts files.
    """
    keys = get_default_host_keys()
    if not keys.has_key(hostname):
        _logger.error('Remote server returned no host key!')
    elif not keys[hostname].has_key(key.get_name()):
        _logger.error('Remote server host key unknown!')
    elif keys[hostname][key.get_name()] != key:
        _logger.error('Remote server host key changed!')
    else:
        _logger.info('Remote server host key is valid.')
        return True
    return False


def open_socket(hostname, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        return sock
    except Exception, e:
        _logger.exception('Cannot connect to host=%s port=%d' % (
                hostname, port))
        raise


def get_default_private_RSA():
    path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
    try:
        key = paramiko.RSAKey.from_private_key_file(path)
        return key
    except paramiko.PasswordRequiredException:
        _logger.info('could not auth passwordless with RSA key %s' % path)

def get_default_private_DSA():
    path = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa')
    try:
        key = paramiko.DSAKey.from_private_key_file(path)
        return key
    except paramiko.PasswordRequiredException:
        _logger.info('could not auth passwordless with DSA key %s' % path)


def get_default_private_key():
    key = get_default_private_RSA()
    if None == key:
        key = get_default_private_DSA()
    return key



def connect_to_host(conf_vars):
    """Open a transport connection and authentificate.

    Return a reference to the open connection.
    """
    default_ssh_port = 22
    hostname = conf_vars['RemoteHostname']
    username = conf_vars['RemoteUsername']

    sock = open_socket(hostname, default_ssh_port)
    t = paramiko.Transport(sock)
    try:
        try:
            t.start_client()
        except paramiko.SSHException:
            _logger.exception('Cannot negociate SSH protocol for host=%s port=%d' % (
                    hostname, default_ssh_port))
            raise
        remotekey = t.get_remote_server_key()
        if not is_remote_server_key_known(remotekey, hostname):
            raise Exception, 'Cannot validate remote host key'
        key = get_default_private_key()
        t.auth_publickey(username, key)
        return t
    except:
        t.close()




def transfer_files(files, conf_vars):
    t = connect_to_host(conf_vars)
    try:
        if len(files) > 0:
            _logger.debug('before mk SFTPClient')
            sftp = paramiko.SFTPClient.from_transport(t)
            _logger.debug('after  mk SFTPClient')
            for fpath in files:
                print "-------", fpath
                # extract the name of the file from the path
                fname = os.path.basename(fpath)
                print "-------NAME: ", fname
                # append the name to the destination
                fdest = os.path.join(conf_vars['RepoPath'], fname)
                print "-------dest: ", fdest
                _logger.debug('PUTTING: local:[%s] remote:[%s]' % (fpath, fdest))
                sftp.put(fpath, fdest)
    except:
        _logger.exception('error while transferring files with paramiko')
    finally:
        t.close()

def print_usage():
    print 'Usage: %s config_file [files to send to storer]' % sys.argv[0]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _setup_logging()
    if len(sys.argv) < 2:
        print 'No config file given'
        print_usage()
        exit(1)

    config_path = sys.argv[1]
    conf_vars = config_variables(config_path)
    files = sys.argv[2:]
    print '[CALLBACK] files = %s' % str(files)
    transfer_files(files, conf_vars)
    print '[CALLBACK] YEAH! Callback ran! sys.argv[] = %s' % str(sys.argv)
    print '[CALLBACK] test vmcheckerpaths-root: %s ' % vmcheckerpaths.root()
