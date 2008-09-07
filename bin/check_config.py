#! /usr/bin/python

from __future__ import with_statement


__author__ = 'Ana Savu ana.savu86@gmail.com'


import time
import sys
import misc
import ConfigParser
import subprocess
import os
import shutil


def main():
    if len(sys.argv) != 4:
        print >> sys.stderr, 'Usage: %s user_id assignment_id archive_path' % sys.argv[0]
        sys.exit(1)

    course_config_file = misc.config_file()

    user_id = sys.argv[1]             # student name
    job = sys.argv[2]                 # assignment name
    archive_path = sys.argv[3]        # archive path

    global_config_file = ConfigParser.RawConfigParser()
    global_config_file.readfp(open(course_config_file))

    # parses global course configuration file
    course_name = global_config_file.get('DEFAULT', 'CourseName')

    tester = global_config_file.get(job, 'Tester')
    vmname = global_config_file.get(job, 'VMName')
    deadline = global_config_file.get(job, 'Deadline')
    kernel_msg = misc.get_option(global_config_file, job, 'KernelMsg')

    # the upload time is the system's current time
    upload_time = time.strftime("%d-%m-%y %H:%M:%S")

    hw_path = os.path.join(misc.vmchecker_root(), 'back', job, user_id, upload_time)
    os.makedirs(hw_path)

    hw_path = os.path.join(hw_path, 'file.zip')
    shutil.copy(archive_path, hw_path)

    # assignment configuration file
    file = '[DEFAULT]\n'
    file += 'Job=%s\n' % job
    file += 'UserId=%s\n' % user_id
    file += 'VMCheckerRoot=%s\n' % misc.vmchecker_root()
    file += 'Tester=%s\n' % tester
    file += 'VMName=%s\n' % vmname
    file += 'Deadline=%s\n' % deadline
    file += 'UploadTime=%s\n' % upload_time
    file += 'KernelMsg=%s\n' % kernel_msg

    job_config_file = os.path.join(
        misc.vmchecker_root(), 'unchecked',
        '%s %s %s.ini' % (upload_time, user_id, job))

    assert os.path.isdir(os.path.dirname(job_config_file)), (
        'Directorul pentru fisierul de configurare (%s) a temei nu exista' % (
            os.path.dirname(job_config_file)))

    with open(job_config_file, 'w') as handle:
        handle.write(file)
        handle.flush()

    # call remote_check script
    remote_check = os.path.join(os.path.dirname(sys.argv[0]), 'remote_check.py')
    try:
        return_code = subprocess.call([remote_check, job_config_file])
    except OSError, e:
        print >> sys.stderr, 'Nu pot invoca %s (%s)' % (remote_check, str(e))

    if return_code != 0:
        print >> sys.stderr, 'Programul %s a esuat' % remote_check
        sys.exit(1)


if __name__ == '__main__':
    main()

