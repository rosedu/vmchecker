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

from vmchecker import paths, update_db, penalty, submissions, submit, coursedb
from vmchecker.coursedb import opening_course_db
from vmchecker.courselist import CourseList
from vmchecker.config import LdapConfig, StorerCourseConfig

try:
    import simplejson as json
except ImportError:
    import json

# If requested, remember user for up to two weeks
EXTENDED_SESSION_TIMEOUT = 60 * 60 * 24 * 14;

# .vmr files may be very large because of errors in the student's submission.
MAX_VMR_FILE_SIZE = 5 * 1024 * 1024 # 500 KB

# define ERROR_MESSAGES
ERR_AUTH = 1
ERR_EXCEPTION = 2
ERR_OTHER = 3

# define MD5 processing errors
MD5_ERR_BAD_MD5 = 'md5'
MD5_ERR_BAD_ZIP = 'zip'


# I18N support
import gettext
# NOTE: This is where the locale files are installed by default.
# Ideally this shouldn't be hardcoded, but it will do for now.
DEFAULT_LOCALE_PATH="/usr/local/share/locale"
DEFAULT_LOCALE="en"
lang_en = gettext.translation("vmchecker", DEFAULT_LOCALE_PATH, languages=["en"])
lang_fr = gettext.translation("vmchecker", DEFAULT_LOCALE_PATH, languages=["fr"])
lang_ro = gettext.translation("vmchecker", DEFAULT_LOCALE_PATH, languages=["ro"])

def install_i18n(lang):
    if lang == "en":
        lang_en.install()
    elif lang == "ro":
        lang_ro.install()
    elif lang == "fr":
        lang_fr.install()
    else:
        lang_en.install()
# End I18N support


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
        vmpaths = paths.VmcheckerPaths(StorerCourseConfig(coursecfg_fname).root_path())
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
    if not ldap_cfg.bind_anonymous():
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
    if not ldap_cfg.bind_anonymous():
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



def submission_upload_info(vmcfg, courseId, assignment, account, isTeamAccount, isGraded):
    """Return a string explaining the submission upload time, deadline
    and the late submission penalty
    """

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    sbroot = vmpaths.dir_cur_submission_root(assignment, account)
    grade_file = paths.submission_results_grade(sbroot)
    sbcfg = paths.submission_config_file(sbroot)
    if not os.path.exists(sbcfg):
        return _("No submission exists for this assignment")

    late_penalty = update_db.compute_late_penalty(assignment, account, vmcfg)
    ta_penalty   = update_db.compute_TA_penalty(grade_file)
    deadline_str = vmcfg.assignments().get(assignment, 'Deadline')
    total_points = int(vmcfg.assignments().get(assignment, 'TotalPoints'))
    deadline_struct = time.strptime(vmcfg.assignments().get(assignment, 'Deadline'),
                                    penalty.DATE_FORMAT)
    sss = submissions.Submissions(vmpaths)
    upload_time_str = sss.get_upload_time_str(assignment, account)
    upload_time_struct = sss.get_upload_time_struct(assignment, account)

    deadline_explanation = penalty.verbose_time_difference(upload_time_struct, deadline_struct)

    submitter_explanation = None
    if isTeamAccount:
        submitter_explanation = _("Submitted by") + ": " + sss.get_submitting_user(assignment, account)

    max_line_width = 0
    rows_to_print = []

    if isTeamAccount:
        rows_to_print += [
            [ submitter_explanation ],
            [ '' ]
        ]

    rows_to_print += [
        [ _("Submission date"), upload_time_str ],
        [ _("Assignment deadline"), deadline_str ],
        [ deadline_explanation ]
    ]

    if isGraded or not vmcfg.assignments().is_deadline_hard(assignment):
        rows_to_print += [
            [ '' ]
        ]

    if not vmcfg.assignments().is_deadline_hard(assignment):
        rows_to_print += [
            [ _("Penalty (late submission)"), str(late_penalty) ],
        ]

    if isGraded:
        rows_to_print += [
            [ _("Penalty (grading)"), str(ta_penalty) ],
            [ _("Penalty (total)"), str(ta_penalty + late_penalty) ],
            [ '' ],
            [ _("Grade"), str(total_points + ta_penalty + late_penalty) ]
        ]

    for row in rows_to_print:
        row[0] = row[0].decode("utf-8")
        if len(row) == 2 and len(row[0]) > max_line_width:
            max_line_width = len(row[0])

    if isGraded:
        # Put a dashed line just above the 'Grade' line
        rows_to_print[len(rows_to_print) - 2][0] = '-' * max_line_width

    ret = u""
    for row in rows_to_print:
        if len(row) == 1:
            ret += row[0] + "\n"
        elif len(row) == 2:
            ret += unicode("{0[0]:<" + str(max_line_width) + "} : {0[1]}\n").format(row)

    ret += "\n"

    return ret



def sortResultFiles(rfiles):
    """Sort the vector of result files and change keys with human
    readable descriptions"""

    file_descriptions = [
        {'fortune.vmr'          : _('Results not yet available')},
        {'grade.vmr'            : _('Grade')},
        {'submission.vmr'       : _('Submission info')},
        {'build-stdout.vmr'     : _('Compilation (stdout)')},
        {'build-stderr.vmr'     : _('Compilation (stderr)')},
        {'run-stdout.vmr'       : _('Testing (stdout)')},
        {'run-stderr.vmr'       : _('Testing (stderr)')},
        {'run-km.vmr'           : _('Kernel messages(netconsole)')},
        {'queue-contents.vmr'   : _('Testing queue')},
        {'vmchecker-stderr.vmr' : _('Errors')},
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


def get_test_queue_contents(vmcfg, courseId):
    """Get the contents of the test queues for all testers configured
    in the system."""
    try:
        tstcfg = vmcfg.testers()
        queue_contents = {} # dict of strings
        for tester_id in tstcfg:
            queue_contents[tester_id] = submit.get_tester_queue_contents(vmcfg, tester_id)

        # print the concatenation of all 'ls' instances
        return json.dumps(queue_contents, indent=4)
    except:
        strout = OutputString()
        traceback.print_exc(file = strout)
        return json.dumps({'errorTrace' : strout.get()}, indent=4)




def get_storagedir_contents(courseId, assignmentId, account):
    """Get the content of a the archive coresponding to a
    MD5Submission-type homework"""
    client = paramiko.SSHClient()
    try:
        vmcfg = StorerCourseConfig(CourseList().course_config(courseId))
        assignments = vmcfg.assignments()
        storage_hostname = assignments.get(assignmentId, 'AssignmentStorageHost')
        storage_username = assignments.get(assignmentId, 'AssignmentStorageQueryUser')
        storage_basepath = assignments.storage_basepath(assignmentId, account)

        client.load_system_host_keys(vmcfg.known_hosts_file())
        client.connect(storage_hostname,
                       username=storage_username,
                       key_filename=vmcfg.storer_sshid(),
                       look_for_keys=False)

        cmd = "find " + storage_basepath + '/' + account + \
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

def validate_md5_submission(courseId, assignmentId, account, archiveFileName):
    """Checks whether a MD5Submission is valid:
       * checks that the uploaded md5 corresponds to the one of the machine
       * checks that the archive uploaded by the student is a zip file

       On success returns (True,).
       On failure reports the source of the failure:
       - (False, 'md5') - the uploaded md5 does not match the one computed on the archive
       - (False, 'zip') - the uploaded archive is not zip.
    """

    md5_calculated = ""
    md5_uploaded = ""
    archive_file_type = ""

    client = paramiko.SSHClient()
    try:
        vmcfg = StorerCourseConfig(CourseList().course_config(courseId))
        assignments = vmcfg.assignments()
        storage_hostname = assignments.get(assignmentId, 'AssignmentStorageHost')
        storage_username = assignments.get(assignmentId, 'AssignmentStorageQueryUser')
        storage_basepath = assignments.storage_basepath(assignmentId, account)

        client.load_system_host_keys(vmcfg.known_hosts_file())
        client.connect(storage_hostname,
                       username=storage_username,
                       key_filename=vmcfg.storer_sshid(),
                       look_for_keys=False)

        archive_abs = os.path.join(storage_basepath, account, archiveFileName)

        # XXX: This will take ages to compute! I wonder how many
        # connections will Apache hold.
        stdin, stdout, stderr = client.exec_command("md5sum " + QuoteForPOSIX(archive_abs))
        md5_calculated = stdout.readline().split()[0]
        for f in [stdin, stdout, stderr]: f.close()

        stdin, stdout, stderr = client.exec_command("file " + QuoteForPOSIX(archive_abs))
        archive_file_type = stdout.readline()[len(archive_abs):].split()[1].lower()
        for f in [stdin, stdout, stderr]: f.close()


        vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
        submission_dir = vmpaths.dir_cur_submission_root(assignmentId, account)
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
        return (False, MD5_ERR_BAD_MD5) # report the type of the problem

    if not archive_file_type == "zip":
        return (False, MD5_ERR_BAD_ZIP) # report the type of the problem


    return (True,) # no problemo

# Service method helpers
def getUserUploadedMd5Helper(courseId, assignmentId, username, strout):
    """Get the current MD5 sum submitted for a given username on a given assignment"""
    try:
        vmcfg = config.StorerCourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    (_, account) = getAssignmentAccountName(courseId, assignmentId, username, strout)
    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    submission_dir = vmpaths.dir_cur_submission_root(assignmentId, account)
    md5_fpath = paths.submission_md5_file(submission_dir)

    md5_result = {}
    try:
        if os.path.exists(paths.submission_config_file(submission_dir)) and os.path.isfile(md5_fpath):
            sss = submissions.Submissions(vmpaths)
            upload_time_str = sss.get_upload_time_str(assignmentId, account)
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

def getAssignmentAccountName(courseId, assignmentId, username, strout):
    try:
        vmcfg = StorerCourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    with opening_course_db(vmpaths.db_file()) as course_db:
        # First check if the user is part of a team for this assignment
        user_team = course_db.get_user_team_for_assignment(assignmentId, username)
        if user_team == None:
            # No team, so just use the user's own account
            return (False, username)
        else:
            # Check if this team has a mutual account
            mutual_account = course_db.get_team_has_mutual_account(user_team)
            if mutual_account:
                return (True, user_team)
            else:
                return (False, username)

def getResultsHelper(courseId, assignmentId, currentUser, strout, username = None, teamname = None, currentTeam = None):
    # assume that the session was already checked

    if username != None and teamname != None:
        return json.dumps({'errorType' : ERR_OTHER,
                           'errorMessage' : "Can't query both user and team results at the same time.",
                           'errorTrace' : ""})


    try:
        vmcfg = StorerCourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    # Check if the current user is allowed to view any other user's grade.
    # TODO: This should be implemented neater using some group
    # and permission model.

    is_authorized = vmcfg.public_results() or \
                    currentUser in vmcfg.admin_list() or \
                    username == currentUser or \
                    teamname == currentTeam

    if not is_authorized:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "User is not authorized to view results.",
                           'errorTrace' : strout.get()})

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())

    account = None
    if username != None:
        # Check if the user is part of a team with a mutual account for this submission
        (isTeamAccount, account) = getAssignmentAccountName(courseId, assignmentId, username, strout)
    else:
        account = teamname
        isTeamAccount = True

    submission_dir = vmpaths.dir_cur_submission_root(assignmentId, account)

    r_path = paths.dir_submission_results(submission_dir)

    assignments = vmcfg.assignments()
    ignored_vmrs = assignments.ignored_vmrs(assignmentId)
    try:
        isGraded = False
        result_files = []
        if os.path.isdir(r_path):
            update_db.update_grades(courseId, account=account, assignment=assignmentId)
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
                        overflow_msg = '\n\n' + _('File truncated! Actual size') + ': ' + str(f_size) + ' ' + _('bytes') + '\n'
                    # decode as utf-8 and ignore any errors, because
                    # characters will be badly encoded as json.
                    with codecs.open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(MAX_VMR_FILE_SIZE) + overflow_msg
                        content = xssescape(content)
                        result_files.append({fname : content})
                        if fname == 'grade.vmr' and \
                                "".join(content.split()) not in submissions.GENERATED_STATUSES:
                            isGraded = True
        if (len(result_files) == 1 and result_files[0].keys()[0] == "grade.vmr") and \
                not vmcfg.assignments().submit_only(assignmentId):
            msg = _("In the meantime have a fortune cookie") + ": <blockquote>"
            try:
                process = subprocess.Popen('/usr/games/fortune',
                                       shell=False,
                                       stdout=subprocess.PIPE)
                msg += process.communicate()[0] + "</blockquote>"
            except:
                msg += "Knock knock. Who's there? [Silence] </blockquote>"
            result_files = [ {'fortune.vmr' :  msg } ]
            result_files.append({'queue-contents.vmr' :  get_test_queue_contents(vmcfg, courseId) })
        if 'submission.vmr' not in ignored_vmrs:
            result_files.append({'submission.vmr' :
                                 submission_upload_info(vmcfg, courseId, assignmentId, account, isTeamAccount, isGraded)})
        result_files = sortResultFiles(result_files)
        return json.dumps(result_files)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

def getAllGradesHelper(courseId, username, strout):
    try:
        # XXX: DON'T DO THIS: performance degrades very much!
        #update_db.update_grades(courseId)
        vmcfg = StorerCourseConfig(CourseList().course_config(courseId))
        vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
        assignments = vmcfg.assignments()
        sorted_assg = sorted(assignments, lambda x, y: int(assignments.get(x, "OrderNumber")) -
                                                       int(assignments.get(y, "OrderNumber")))

        # Check if the current user is allowed to view all the grades
        # TODO: This should be implemented neater using some group
        # and permission model.

        user_can_view_all = False
        if vmcfg.public_results() or username in vmcfg.admin_list():
            user_can_view_all = True

        user_grade_rows = None
        team_grade_rows = None
        with opening_course_db(vmpaths.db_file()) as course_db:
            if user_can_view_all:
                user_grade_rows = course_db.get_user_grades()
                team_grade_rows = course_db.get_team_grades()
            else:
                # Get all the individual grades that the user is allowed to see
                user_grade_rows = course_db.get_user_and_teammates_grades(username)
                # Get all the team grades that the user is allowed to see
                team_grade_rows = course_db.get_user_team_grades(user = username)

        ret = []
        grades = {}
        for row in user_grade_rows:
            user, assignment, grade = row
            if not assignment in vmcfg.assignments():
                continue
            if not vmcfg.assignments().show_grades_before_deadline(assignment):
                deadline = time.strptime(vmcfg.assignments().get(assignment, 'Deadline'), DATE_FORMAT)
                deadtime = time.mktime(deadline)
                if time.time() < deadtime:
                    continue
            if vmcfg.assignments().is_hidden(assignment) and username not in vmcfg.admin_list():
                continue

            grades.setdefault(user, {})[assignment] = grade

        for user in sorted(grades.keys()):
            ret.append({'gradeOwner' : 'user',
                        'name'       : user,
                        'results'    : grades.get(user)})

        grades = {}
        for row in team_grade_rows:
            team, assignment, grade = row
            if not assignment in vmcfg.assignments():
                continue
            if not vmcfg.assignments().show_grades_before_deadline(assignment):
                deadline = time.strptime(vmcfg.assignments().get(assignment, 'Deadline'), DATE_FORMAT)
                deadtime = time.mktime(deadline)
                if time.time() < deadtime:
                    continue
            grades.setdefault(team, {})[assignment] = grade

        for team in sorted(grades.keys()):
            ret.append({'gradeOwner' : 'team',
                        'name'       : team,
                        'results'    : grades.get(team)})
        return json.dumps(ret)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

def getUserStorageDirContentsHelper(courseId, assignmentId, username, strout):
    """Get the current files in the home directory on the storage host for a given username"""
    (_, account) = getAssignmentAccountName(courseId, assignmentId, username, strout)
    try:
        result = get_storagedir_contents(courseId, assignmentId, account)
        return result
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})


class InvalidDataException(Exception):
    pass

import re

courseIdRegex = re.compile('^[a-zA-Z0-9]+$')
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

localeRegexWhiteList = re.compile('^[a-z]{2}$')
def sanityCheckLocale(locale):
    if localeRegexWhiteList.match(locale) is None:
        raise InvalidDataException
    return locale
