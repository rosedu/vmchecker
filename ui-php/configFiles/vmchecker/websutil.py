#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement


import os
import ldap
import time
import paramiko
import traceback

from vmchecker import paths, update_db, penalty, submissions
from vmchecker.courselist import CourseList
from vmchecker.config import LdapConfig, CourseConfig

try:
    import simplejson as json
except ImportError:
    import json


class OutputString():
    def __init__(self):
        self.st = ""

    def write(self, st):
        self.st += st

    def get(self):
        return self.st


def get_user(username, password):
    """Find the username for a user based on username/password.

    This searches LDAP or some file-based json files in the user's
    home directories.

    Returns the username on success.
    """

    # allthough a misconfigured user can block access to any course,
    # we preffer early LOUD errors to silently ignored ones.
    # Fail fast, fail lowdly!
    r = get_user_from_auth_files(username, password)
    if not r is None:
        return r
    return get_ldap_user(username, password)


def get_user_from_auth_files(username, password):
    """Search all courseses for auth_files and if we can login in any
    course, return the login from there"""
    for coursecfg_fname in CourseList().course_configs():
        vmpaths = paths.VmcheckerPaths(CourseConfig(coursecfg_fname).root_path())
        r = get_user_from_auth_file(vmpaths, username, password)
        if not r is None:
            return r
    return None



def get_user_from_auth_file(vmpaths, username, password):
    """Try to authenticate using one course's auth_file.

    Return the username on success.
    """
    if not os.path.exists(vmpaths.auth_file()):
        return None
    with open(vmpaths.auth_file()) as handle:
        auth_file_contents =  handle.read()
        auth_dic = json.loads(auth_file_contents)['auth']
    if auth_dic.has_key(username) and auth_dic[username] == password:
        return username
    return None


def get_ldap_user(username, password):
    """Try to authenticate using the global LDAP configuration file.

    Return the username on success.
    """
    ldap_cfg = LdapConfig()
    con = ldap.initialize(ldap_cfg.server())
    con.simple_bind_s(ldap_cfg.bind_user(),
                        ldap_cfg.bind_pass())

    baseDN = ldap_cfg.root_search()
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None

    # XXX : Needs sanitation
    searchFilter = '(uid=' + username + ')'

    timeout = 0
    count = 0

    # find the user's dn
    result_id = con.search(baseDN,
                        searchScope,
                        searchFilter,
                        retrieveAttributes)
    result_set = []
    while 1:
        result_type, result_data = con.result(result_id, timeout)
        if (result_data == []):
            break
        else:
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)

    if len(result_set) == 0:
        #no results
        return None

    if len(result_set) > 1:
        # too many results for the same uid
        raise

    user_dn, entry = result_set[0][0]
    con.unbind_s()

    # check the password
    try:
        con = ldap.initialize(ldap_cfg.server())
        con.simple_bind_s(user_dn, password)
    except ldap.INVALID_CREDENTIALS:
        return None
    except:
        raise

    return entry['cn'][0]


# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def _find_file(searched_file_name, rfiles):
    """Search for a filename in an array for {fname:fcontent} dicts"""
    for rfile in rfiles:
        if rfile.has_key(searched_file_name):
            return rfile
    return None



def submission_upload_info(courseId, user, assignment):
    """Return a string explaining the submission upload time, deadline
    and the late submission penalty
    """
    vmcfg = CourseConfig(CourseList().course_config(courseId))
    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    sbroot = vmpaths.dir_cur_submission_root(assignment, user)
    grade_file = paths.submission_results_grade(sbroot)
    sbcfg = paths.submission_config_file(sbroot)
    if not os.path.exists(sbcfg):
        return "Tema nu a fost încă trimisă"

    late_penalty = update_db.compute_late_penalty(assignment, user, vmcfg)
    ta_penalty   = update_db.compute_TA_penalty(grade_file)
    deadline_str = vmcfg.assignments().get(assignment, 'Deadline')
    total_points = int(vmcfg.assignments().get(assignment, 'TotalPoints'))
    deadline_struct = time.strptime(vmcfg.assignments().get(assignment, 'Deadline'),
                                    penalty.DATE_FORMAT)
    sss = submissions.Submissions(vmpaths)
    upload_time_str = sss.get_upload_time_str(assignment, user)
    upload_time_struct = sss.get_upload_time_struct(assignment, user)

    deadline_explanation = penalty.verbose_time_difference(upload_time_struct, deadline_struct)

    ret = ""
    ret += "Data trimiterii temei : " + upload_time_str + "\n"
    ret += "Deadline temă         : " + deadline_str    + "\n"
    ret += deadline_explanation + "\n"
    ret += "\n"
    ret += "Depunctare întârziere : " + str(late_penalty) + "\n"
    ret += "Depunctare corectare  : " + str(ta_penalty)   + "\n"
    ret += "Total depunctări      : " + str(ta_penalty + late_penalty) + "\n"
    ret += "-----------------------\n"
    ret += "Nota                  : " + str(total_points + ta_penalty + late_penalty) + "\n"
    ret += "\n"

    return ret



def sortResultFiles(rfiles):
    """Sort the vector of result files and change keys with human
    readable descriptions"""

    file_descriptions = [
        {'fortune.vmr'          : 'Rezultatele nu sunt încă disponibile'},
        {'grade.vmr'            : 'Nota și observații'},
        {'late-submission.vmr'  : 'Date și depunctări'},
        {'vmchecker-stderr.vmr' : 'Erori vmchecker'},
        {'build-stdout.vmr'     : 'Compilarea temei și a testelor (stdout)'},
        {'build-stderr.vmr'     : 'Compilarea temei și a testelor (stderr)'},
        {'run-stdout.vmr'       : 'Execuția testelor (stdout)'},
        {'run-stderr.vmr'       : 'Execuția testelor (stderr)'},
        {'run-km.vmr'           : 'Mesaje kernel (netconsole)'},
        {'queue-contents.vmr'   : 'Coada temelor ce urmează să fie testate'},
        ]
    ret = []
    for f_des in file_descriptions:
        key = f_des.keys()[0] # there is only one key:value pair in each dict
        rfile = _find_file(key, rfiles)
        if rfile == None:
            continue
        else:
            ret.append({f_des.get(key) : rfile.get(key)})
            rfiles.remove(rfile)
    ret += rfiles
    return ret


def get_test_queue_contents(courseId):
    """Get the contents of the test queues for all testers configured
    in the system."""
    try:
        vmcfg = CourseConfig(CourseList().course_config(courseId))
        tstcfg = vmcfg.testers()
        queue_contents = [] # array of strings

        for tester_id in tstcfg:
            # connect to the tester
            client = paramiko.SSHClient()
            try:
                client.load_system_host_keys(vmcfg.known_hosts_file())
                client.connect(tstcfg.hostname(tester_id),
                               username=tstcfg.login_username(tester_id),
                               key_filename=vmcfg.storer_sshid(),
                               look_for_keys=False)

                # run 'ls' in the queue_path and get it's output.
                cmd = 'ls -ctgG ' + tstcfg.queue_path(tester_id)
                stdin, stdout, stderr = client.exec_command(cmd)
                data = stdout.readlines()
                for f in [stdin, stdout, stderr]: f.close()
                if len(data) > 0:
                    data = data[1:]
                    queue_contents.append(data)

            finally:
                client.close()

        # print the concatenation of all 'ls' instances
        return json.dumps(queue_contents, indent=4)
    except:
        strout = OutputString()
        traceback.print_exc(file = strout)
        return json.dumps({'errorTrace' : strout.get()}, indent=4)




def get_storagedir_contents(courseId, assignmentId, username):
    """Get the content of a the archive coresponding to a
    MD5Submission-type homework"""
    client = paramiko.SSHClient()
    try:
        vmcfg = CourseConfig(CourseList().course_config(courseId))
        assignments = vmcfg.assignments()
        storage_hostname = assignments.get(assignmentId, 'AssignmentStorageHost')
        storage_username = assignments.get(assignmentId, 'AssignmentStorageQueryUser')
        storage_basepath = assignments.storage_basepath(assignmentId, username)

        client.load_system_host_keys(vmcfg.known_hosts_file())
        client.connect(storage_hostname,
                       username=storage_username,
                       key_filename=vmcfg.storer_sshid(),
                       look_for_keys=False)

        cmd = "find " + storage_basepath + '/' + username + \
            " \( ! -regex '.*/\..*' \) -type f"

        stdin, stdout, stderr = client.exec_command(cmd)
        result = []
        for d in stdout.readlines():
            result.append({'fileName' : d})
        for f in [stdin, stdout, stderr]: f.close()

        return json.dumps(result)
    except:
        strout = OutputString()
        traceback.print_exc(file = strout)
        return json.dumps({'errorTrace' : strout.get()}, indent=4)
    finally:
        client.close()

def QuoteForPOSIX(string):
    return "\\'".join("'" + p + "'" for p in string.split("'"))

def validate_md5_submission(courseId, assignmentId, username, archiveFileName):
    """Checks whether a MD5Submission is valid:
       * checks that the uploaded md5 corresponds to the one of the machine
       * checks that the archive uploaded by the student is a zip file

       On success returns 'ok'.
       On failure reports the source of the failure:
       - 'md5' - the uploaded md5 does not match the one computed on the archive
       - 'zip' - the uploaded archive is not zip.
    """

    md5_calculated = ""
    md5_uploaded = ""
    archive_file_type = ""

    client = paramiko.SSHClient()
    try:
        vmcfg = CourseConfig(CourseList().course_config(courseId))
        assignments = vmcfg.assignments()
        storage_hostname = assignments.get(assignmentId, 'AssignmentStorageHost')
        storage_username = assignments.get(assignmentId, 'AssignmentStorageQueryUser')
        storage_basepath = assignments.storage_basepath(assignmentId, username)

        client.load_system_host_keys(vmcfg.known_hosts_file())
        client.connect(storage_hostname,
                       username=storage_username,
                       key_filename=vmcfg.storer_sshid(),
                       look_for_keys=False)

        archive_abs = os.path.join(storage_basepath, username, archiveFileName)

        # XXX: This will take ages to compute! I wonder how many
        # connections will Apache hold.
        stdin, stdout, stderr = client.exec_command("md5sum " + QuoteForPOSIX(archive_abs))
        md5_calculated = stdout.readline().split()[0]
        for f in [stdin, stdout, stderr]: f.close()

        stdin, stdout, stderr = client.exec_command("file " + QuoteForPOSIX(archive_abs))
        archive_file_type = stdout.readline()[len(archive_abs):].split()[1].lower()
        for f in [stdin, stdout, stderr]: f.close()


        vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
        submission_dir = vmpaths.dir_cur_submission_root(assignmentId, username)
        md5_fpath = paths.submission_md5_file(submission_dir)

        if os.path.isfile(md5_fpath):
            with open(md5_fpath, 'r') as f:
                md5_uploaded = f.read(32)
    except:
        strout = OutputString()
        traceback.print_exc(file = strout)
        return json.dumps({'errorTrace' : strout.get()}, indent=4)
    finally:
        client.close()

    if not md5_calculated == md5_uploaded:
        return "md5" # report the type of the problem

    if not archive_file_type == "zip":
        return "zip" # report the type of the problem


    return "ok" # no problemo

