#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement


import os
import ldap
import time
import paramiko
import traceback
import codecs
import subprocess
from cgi import escape

from vmchecker import paths, update_db, penalty, submissions
from vmchecker.courselist import CourseList
from vmchecker.config import LdapConfig, CourseConfig

try:
    import simplejson as json
except ImportError:
    import json

# .vmr files may be very large because of errors in the student's submission.
MAX_VMR_FILE_SIZE = 500 * 1024 # 500 KB

# define ERROR_MESSAGES
ERR_AUTH = 1
ERR_EXCEPTION = 2
ERR_OTHER = 3



class OutputString():
    def __init__(self):
        self.st = ""

    def write(self, st):
        self.st += st

    def get(self):
        return self.st

def xssescape(text):
    """Gets rid of < and > and & and, for good measure, :"""
    return escape(text, quote=True).replace(':','&#58;')

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
    try:
        r = get_ldap_user(username, password)
    except:
        r = None
    return r


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

    # XXX hack, we should move this
    language = 'ro'
    deadline_explanation = penalty.verbose_time_difference(upload_time_struct, deadline_struct, language)

    ret = ""

    if language is 'ro':
        ret += "Data trimiterii temei : " + upload_time_str + "\n"
        ret += "Deadline temă         : " + deadline_str    + "\n"
        ret += deadline_explanation + "\n"
        ret += "\n"
        ret += "Depunctare întârziere : " + str(late_penalty) + "\n"
        ret += "Depunctare corectare  : " + str(ta_penalty)   + "\n"
        ret += "Total depunctări      : " + str(ta_penalty + late_penalty) + "\n"
        ret += "-----------------------\n"
        ret += "Nota                  : " + str(total_points + ta_penalty + late_penalty) + "\n"
    else:
        # another language
        ret += "Submision date           : " + upload_time_str + "\n"
        ret += "Assignment deadline      : " + deadline_str    + "\n"
        ret += deadline_explanation + "\n"
        ret += "\n"
        ret += "Penalty (late submission): " + str(late_penalty) + "\n"
        ret += "Penalty (grading)        : " + str(ta_penalty)   + "\n"
        ret += "Penalty (total)          : " + str(ta_penalty + late_penalty) + "\n"
        ret += "---------------------------\n"
        ret += "Grade                    : " + str(total_points + ta_penalty + late_penalty) + "\n"

    ret += "\n"

    return ret



def sortResultFiles(rfiles, language='ro'):
    """Sort the vector of result files and change keys with human
    readable descriptions"""

    file_descriptions_ro = [
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
    file_descriptions_en = [
        {'fortune.vmr'          : 'Results not yet available'},
        {'grade.vmr'            : 'Grade'},
        {'late-submission.vmr'  : 'Penalty points'},
        {'build-stdout.vmr'     : 'Compilation (stdout)'},
        {'build-stderr.vmr'     : 'Compilation (stderr)'},
        {'run-stdout.vmr'       : 'Testing (stdout)'},
        {'run-stderr.vmr'       : 'Testing (stderr)'},
        {'run-km.vmr'           : 'Kernel messages(netconsole)'},
        {'queue-contents.vmr'   : 'Testing queue'},
        {'vmchecker-stderr.vmr' : 'Errors'},
        ]
    file_descriptions = {
            'ro' : file_descriptions_ro,
            'en' : file_descriptions_en,
            }
    ret = []
    for f_des in file_descriptions[language]:
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
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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

# Service method helpers
def getUserUploadedMd5(req, courseId, assignmentId, username):
    """Get the current MD5 sum submitted for a given username on a given assignment"""
    req.content_type = 'text/html'
    strout = OutputString()
    try:
        vmcfg = config.CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    submission_dir = vmpaths.dir_cur_submission_root(assignmentId, username)
    md5_fpath = paths.submission_md5_file(submission_dir)

    strout = OutputString()

    md5_result = {}
    try:
        if os.path.exists(paths.submission_config_file(submission_dir)) and os.path.isfile(md5_fpath):
            sss = submissions.Submissions(vmpaths)
            upload_time_str = sss.get_upload_time_str(assignmentId, username)
            md5_result['fileExists'] = True

            with open(md5_fpath, 'r') as f:
                md5_result['md5Sum'] = f.read(32)

            md5_result['uploadTime'] = upload_time_str
        else:
            md5_result['fileExists'] = False

        return json.dumps(md5_result)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

def getUserResultsHelper(req, courseId, assignmentId, username):
    # assume that the session was already checked

    strout = OutputString()
    try:
        vmcfg = CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    submission_dir = vmpaths.dir_cur_submission_root(assignmentId, username)
    r_path = paths.dir_submission_results(submission_dir)

    assignments = vmcfg.assignments()
    ignored_vmrs = assignments.ignored_vmrs(assignmentId)
    strout = OutputString()
    try:
        result_files = []
        if os.path.isdir(r_path):
            update_db.update_grades(courseId, user=username, assignment=assignmentId)
            for fname in os.listdir(r_path):
                # skill all files not ending in '.vmr'
                if not fname.endswith('.vmr'):
                    continue
                if fname in ignored_vmrs:
                    continue
                f_path = os.path.join(r_path, fname)
                if os.path.isfile(f_path):
                    overflow_msg = ''
                    f_size = os.path.getsize(f_path)
                    if f_size > MAX_VMR_FILE_SIZE:
                        overflow_msg = '\n\n<b>File truncated! Actual size: ' + str(f_size) + ' bytes</b>\n'
                    # decode as utf-8 and ignore any errors, because
                    # characters will be badly encoded as json.
                    with codecs.open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(MAX_VMR_FILE_SIZE) + overflow_msg
                        content = xssescape(content)
                        result_files.append({fname : content})

        if len(result_files) == 0:
            msg = "In the meantime have a fortune cookie: <blockquote>"
            try:
                process = subprocess.Popen('/usr/games/fortune',
                                       shell=False,
                                       stdout=subprocess.PIPE)
                msg += process.communicate()[0] + "</blockquote>"
            except:
                msg += "Knock knock. Who's there? [Silence] </blockquote>"
            result_files = [ {'fortune.vmr' :  msg } ]
            result_files.append({'queue-contents.vmr' :  get_test_queue_contents(courseId) })
        if 'late-submission.vmr' not in ignored_vmrs:
            result_files.append({'late-submission.vmr' :
                                 submission_upload_info(courseId, username, assignmentId)})
        result_files = sortResultFiles(result_files, 'en')
        return json.dumps(result_files)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

def getUserStorageDirContents(req, courseId, assignmentId, username):
    """Get the current files in the home directory on the storage host for a given username"""
    req.content_type = 'text/html'
    strout = OutputString()
    try:
        result = get_storagedir_contents(courseId, assignmentId, username)
        return result
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})


class InvalidDataException(Exception):
    pass

import re

courseIdRegex = re.compile('^[a-zA-Z]+$')
def sanityCheckCourseId(courseId):
    if courseIdRegex.match(courseId) is None:
        raise InvalidDataException
    return courseId

assignmentIdRegex = re.compile('^[0-9a-zA-Z-_]+$')
def sanityCheckAssignmentId(assignmentId):
    if assignmentIdRegex.match(assignmentId) is None:
        raise InvalidDataException
    return assignmentId


dotdotRegexp = re.compile('\.\.')
def sanityCheckDotDot(param):
    if len(dotdotRegexp.findall(param)) != 0:
        raise InvalidDataException
    return param

usernameRegexWhiteList = re.compile('^[a-zA-Z0-9-_.]+$')
def sanityCheckUsername(username):
    if usernameRegexWhiteList.match(username) is None:
        raise InvalidDataException
    sanityCheckDotDot(username)
    return username
