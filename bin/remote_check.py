#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set expandtab :


__author__ = 'Alexandru Mosoi, brtzsnr@gmail.com'


import sys
import os
import subprocess
import ConfigParser

import misc


def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Usage: %s homework_config_file' % sys.argv[0]
        sys.exit(1)

    config_file = misc.config_file()

    homework = ConfigParser.RawConfigParser()
    homework.readfp(open(sys.argv[1]))

    config = ConfigParser.RawConfigParser()
    config.readfp(open(config_file))

    job = homework.get('DEFAULT', 'Job')

    # parses config files and retrieve machine
    remote_ip = misc.get_option(config, job, 'RemoteIP')
    assert remote_ip, 'No ip for remote machine'
    remote_queue = misc.get_option(config, job, 'RemoteQueue')
    assert remote_queue, 'No queue on testing machine supplied'
    remote_user = misc.get_option(config, job, 'RemoteUser')
    assert remote_user, 'No remote user supplied'
    remote_notifier = misc.get_option(config, job, 'RemoteNotifier')
    assert remote_notifier, 'No notifier supplied'

    # invokes scp and copy homework on testing machines
    return_code = subprocess.call([
        'scp',           # program to invoke
        sys.argv[1],     # config file to copy
        '%s@%s:%s' % (remote_user, remote_ip, remote_queue)])
    if return_code != 0:
        print >> sys.stderr, 'Eroare la copierea temei pe masina de testare'
        sys.exit(1)

    # invokes notifier program on testing machine
    course = config.get('DEFAULT', 'CourseName')
    assert course, 'Uknown course...'

    return_code = subprocess.call([
        'ssh',
        '%s@%s' % (remote_user, remote_ip),
        'bash -c "cd %s && %s %s"' % (remote_queue, remote_notifier, course)])
    if return_code != 0:
        print >> sys.stderr, 'Nu am putut invoca programul de notificare'
        sys.exit(1)

    print >> sys.stderr, 'Tema a fost copiata cu succes'


if __name__ == '__main__':
    main()
