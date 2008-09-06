#! /usr/bin/python

from __future__ import with_statement


__author__ = 'Ana Savu ana.savu86@gmail.com'


import time
import sys
import misc
import ConfigParser
import subprocess
import os


def main():
    if len(sys.argv) != 5:
        print >> sys.stderr, 'Usage: %s user_id assignment_id archive_path results_path' % sys.argv[0]
        sys.exit(1)

    course_config_file = misc.config_file()

    user_id = sys.argv[1]             # student name
    job = sys.argv[2]                 # assignment name
    archive_path = sys.argv[3]        # path to atchive
    results_path = sys.argv[4]        # path to check results

    global_config_file = ConfigParser.RawConfigParser()
    global_config_file.readfp(open(course_config_file))

    # parses global course configuration file
    course_name = global_config_file.get('DEFAULT', 'CourseName')
    base_path = global_config_file.get('DEFAULT', 'BasePath')
    penalty = global_config_file.get('DEFAULT', 'Penalty')

    tester = global_config_file.get(job, 'Tester')
    vmname = global_config_file.get(job, 'VMName')
    deadline = global_config_file.get(job, 'Deadline')
    kernel_msg = misc.get_option(global_config_file, job, 'KernelMsg')

    # the upload time is the system's current time
    upload_time = time.strftime("%m-%d-%y %H:%M")

    # assignment configuration file
    job_config_file = os.path.join(
        misc.vmchecker_root(), 'unchecked',
        '%s %s %s.ini' % (upload_time, user_id, job))

    file = '[DEFAULT]\n'
    file += 'Job=%s\n' % job
    file += 'UserId=%s\n' % user_id
    file += 'BasePath=%s\n' % base_path
    file += 'Penalty=%s\n' % penalty
    file += 'Tester=%s\n' % tester
    file += 'VMName=%s\n' % vmname
    file += 'Deadline=%s\n' % deadline
    file += 'UploadTime=%s\n' % upload_time
    file += 'KernelMsg=%s\n' % kernel_msg

    with open(job_config_file, 'w') as handle:
        handle.write(file);

    return_code = subprocess.call([
        './remote_check.py',
        '%s' % job_config_file])
    if return_code != 0:
        print >> sys.stderr, 'Nu am putut invoca programul remote_check'
        sys.exit(1)

if __name__ == '__main__':
    main()
