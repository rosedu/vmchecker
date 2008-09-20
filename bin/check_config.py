#! /usr/bin/python
# Creates a homework configuration file for an upload and calls the 
# remote_check script using this file


from __future__ import with_statement


__author__ = 'Ana Savu ana.savu86@gmail.com'


import ConfigParser
import misc
import os
import pwd
import shutil
import subprocess
import sys
import time


def main():
    # parses arguments
    if len(sys.argv) != 4:
        print >> sys.stderr, 'Usage: %s user_id assignment_id archive_path' % (
                sys.argv[0])
        sys.exit(1)

    user_id = sys.argv[1]             # student name
    job = sys.argv[2]                 # assignment name
    archive_path = sys.argv[3]        # archive path

    course_config_file = misc.config_file()
    global_config_file = ConfigParser.RawConfigParser()
    global_config_file.readfp(open(course_config_file))

    # parses global course configuration file
    course_name = global_config_file.get('DEFAULT', 'CourseName')
    penalty_script = global_config_file.get('DEFAULT', 'PenaltyScript')
    interface = global_config_file.get('DEFAULT', 'Interface') 

    tester = global_config_file.get(job, 'Tester')
    vmname = global_config_file.get(job, 'VMName')
    deadline = global_config_file.get(job, 'Deadline')
    kernel_msg = misc.get_option(global_config_file, job, 'KernelMsg', 
            default='0')

    # copy job files to backup directory
    # the upload time is the system's current time
    upload_time = time.strftime("%d-%m-%y %H:%M:%S")
 
    hw_path = os.path.join(misc.vmchecker_root(), 'back', job, user_id, 
            upload_time)
    os.makedirs(hw_path)
    hw_path = os.path.join(hw_path, 'file.zip')
    shutil.copy(archive_path, hw_path)

    # prepares output directory
    # cleans previous job files
    # output_dir = os.path.join(misc.vmchecker_root(), 'checked', job, user_id)
    # shutil.rmtree(output_dir, ignore_errors=True)
    # os.makedirs(os.path.join(output_dir, 'archive'))

    # writes assignment configuration file
    job_config_file = os.path.join(
        misc.vmchecker_root(), 'unchecked',
        '%s %s %s.ini' % (upload_time, user_id, job))

    assert os.path.isdir(os.path.dirname(job_config_file)), (
        'The configuration file direcotory (%s) does not exist' % (
            os.path.dirname(job_config_file)))

    file = '[DEFAULT]\n'
    file += 'Deadline=%s\n' % deadline
    file += 'Job=%s\n' % job
    file += 'KernelMsg=%s\n' % kernel_msg
    file += 'PenaltyScript=%s\n' % penalty_script
    file += 'Tester=%s\n' % tester
    file += 'UploadTime=%s\n' % upload_time
    file += 'UploaderIP=%s\n' % misc.get_ip_address(interface)
    file += 'UploaderUsername=%s\n' % pwd.getpwuid(os.getuid())[0]
    file += 'UserId=%s\n' % user_id
    file += 'VMCheckerRoot=%s\n' % misc.vmchecker_root()
    file += 'VMName=%s\n' % vmname

    with open(job_config_file, 'w') as handle:
        handle.write(file)
        handle.flush()

    # calls remote_check script
    remote_check = os.path.join(os.path.dirname(sys.argv[0]), 'remote_check.py')
    try:
        return_code = subprocess.call([remote_check, job_config_file])
    except OSError, e:
        print >> sys.stderr, 'Can\'t call %s (%s)' % (remote_check, str(e))

    if return_code != 0:
        print >> sys.stderr, '%s failed' % remote_check
        sys.exit(1)


if __name__ == '__main__':
    main()

