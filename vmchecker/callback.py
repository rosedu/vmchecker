#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Callback script executed on the tester machine
"""
from __future__ import with_statement

import os
import socket
import paramiko
import sys
import ConfigParser

from . import vmlogging

_DEFAULT_SSH_PORT = 22
_logger = vmlogging.create_module_logger('callback')


def _setup_logging():
    """Instruct paramiko to log stuff.
    Should be disabled in production?
    """
    paramiko.util.log_to_file('callback_sftp.log')


def get_default_remote_host_keys():
    """Search for host keys in default paths
    """
    # search two default paths (Linux & Windows)
    search_paths = ['~/.ssh/known_hosts', '~/ssh/known_hosts']
    paths = map(lambda x : os.path.expanduser(x), search_paths)
    for path in paths:
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
    keys = get_default_remote_host_keys()
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
    """Open a connection to the destination machine"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        return sock
    except Exception:
        _logger.exception('Cannot open connection to %s:%d' % (
                hostname, port))
        raise


def get_default_private_RSA():
    """Returns the private RSA key if it exists and can
    be used without a password.
    """
    path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
    try:
        key = paramiko.RSAKey.from_private_key_file(path)
        return key
    except paramiko.PasswordRequiredException:
        _logger.info('could not auth passwordless with RSA key %s' % path)


def get_default_private_DSA():
    """Returns the private DSA key if it exists and can
    be used without a password.
    """
    path = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa')
    try:
        key = paramiko.DSAKey.from_private_key_file(path)
        return key
    except paramiko.PasswordRequiredException:
        _logger.info('could not auth passwordless with DSA key %s' % path)


def get_default_private_key():
    """Returns a private key if one exists and can
    be used without a password.
    """
    key = get_default_private_RSA()
    if None == key:
        key = get_default_private_DSA()
    return key


def connect_to_host(conf_vars):
    """Open a transport connection and authentificate.

    Return a reference to the open connection.
    """
    port = _DEFAULT_SSH_PORT
    host = conf_vars['remotehostname']
    username = conf_vars['remoteusername']

    sock = open_socket(host, port)
    t = paramiko.Transport(sock)
    try:
        try:
            t.start_client()
        except paramiko.SSHException:
            _logger.error(
                    'Cannot negociate SSH protocol with %s:%d.', host, port)
            raise
        remotekey = t.get_remote_server_key()
        if not is_remote_server_key_known(remotekey, host):
            raise RuntimeError('Cannot validate remote host key')
        key = get_default_private_key()
        t.auth_publickey(username, key)
        return t
    except:
        _logger.exception('Connection to %s:%d failed.', host, port)
        t.close()
        raise


def sftp_mkdir_if_not_exits(sftp, dir):
    """If path does not exist mkdir it.
    """
    try:
        sftp.chdir(dir)
    except IOError:
        sftp.mkdir(dir)
        sftp.chdir(dir)


def sftp_transfer_files(sftp, files, conf_vars):
    """Transfers all existing files from the 'files' list
    through sftp.
    """
    for fpath in files:
        # extract the name of the file from the path
        fname = os.path.basename(fpath)
        # append the name to the destination
        fdest = os.path.join(conf_vars['resultsdest'], fname)
        if not os.path.isfile(fpath):
            _logger.info('Could not find file [%s] to transfer' % fpath)
            sftp.open(fdest, 'w').write('-- (could not locate this file on the test vm) --')
        else:
            # actually transfer the files
            _logger.debug('PUTTING: local:[%s] remote:[%s]' % (fpath, fdest))
            sftp.put(fpath, fdest)


def _get_unzipped_local_path(filename):
    """The callback script and filename are sent in a .zip to the
    tester machine. When unzipped they should be in the same directory.
    """
    d = os.path.dirname(sys.argv[0])
    return os.path.normpath(os.path.join(d, filename))


def get_unzipped_local_storer_config():
    """Get the path of the local storer config file."""
    return _get_unzipped_local_path('storer')


def _config_variables(config_file, section_name):
    """Return a dictionary with values from the config_path file.

    NB:  the keys will be all lowercase!
    """
    _config = ConfigParser.RawConfigParser()
    with open(config_file) as handle:
        _config.readfp(handle)
    return dict(_config.items(section_name))


def get_deadline(conf_vars):
    """Return the deadline for the current homework"""
    assignment = conf_vars['assignment']
    storer_config = get_unzipped_local_storer_config()
    # XXX the 'assignment ' + on the next line is a HACK!
    # in the storer config the assignments are stored as 'assignment 1-minishell-linux'
    # but our assignment variable is just '1-minishell-linux'.
    # we shouldn't hardcode 'assignment ' here!
    storer_assignment_vars = _config_variables(storer_config, 'assignment ' + assignment)
    return storer_assignment_vars['deadline']




def send_results_and_notify(files, conf_vars):
    """Opens a connection, transfers files, and
    TODO: calls a script on the storer.
    """
    try:
        t = connect_to_host(conf_vars)
    except:
        _logger.exception('could not connect to remote host')
        return
    try:
        if len(files) > 0:
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp_mkdir_if_not_exits(sftp, conf_vars['resultsdest'])
            sftp_transfer_files(sftp, files, conf_vars)
    except:
        _logger.exception('error while transferring files with paramiko')
    finally:
        t.close()


def print_usage():
    print 'Usage: %s config_file [files to send to storer]' % sys.argv[0]



def run_callback(config_file, files):
    _setup_logging()
    conf_vars = _config_variables(config_file, 'Assignment')
    send_results_and_notify(list(files), conf_vars)


def main():
    if len(sys.argv) < 2:
        print 'No config file given'
        print_usage()
        exit(1)

    config_file = sys.argv[1]
    # skip first two: the script name and the config file :)
    files = sys.argv[2:]
    run_callback(config_file, files)

if __name__ == "__main__":
    main()
