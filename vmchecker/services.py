#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script implements the VMChecker's Web Services.
It's based on apache2 and mod_python.
"""

from __future__ import with_statement

# Use simplejson or Python 2.6 json, prefer simplejson.
try:
    import simplejson as json
except ImportError:
    import json

import os
import sys
import time
import codecs
import sqlite3
import tempfile
import traceback
import subprocess

#from mod_python import Session

from vmchecker.courselist import CourseList
from vmchecker.config import CourseConfig
from vmchecker import submit, config, websutil, update_db, paths, submissions

# .vmr files may be very large because of errors in the student's submission.
MAX_VMR_FILE_SIZE = 500 * 1024 # 500 KB

# define ERROR_MESSAGES
ERR_AUTH = 1
ERR_EXCEPTION = 2 
ERR_OTHER = 3

########## @ServiceMethod
def uploadAssignment(username, courseId, assignmentId, archiveFile):
    strout = websutil.OutputString()
    if archiveFile.filename == None:
        return  json.dumps({'errorType':ERR_OTHER,
                    'errorMessage':"File not uploaded.",
                    'errorTrace':""})

    #  Save file in a temp
    (fd, tmpname) = tempfile.mkstemp('.zip')
    f = open(tmpname, 'wb', 10000)
    ## Read the file in chunks
    for chunk in websutil.fbuffer(archiveFile.file):
        f.write(chunk)
    f.close()
    os.close(fd)

    # Call submit.py
    ## Redirect stdout to catch logging messages from submit
    strout = websutil.OutputString()
    sys.stdout = strout
    try:
        submit.submit(tmpname, assignmentId, username, courseId)
    except submit.SubmittedTooSoonError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"Tema trimisa prea curand",
            'errorTrace':strout.get()})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
    return json.dumps({'status':True,
                       'dumpLog':strout.get()})

########## @ServiceMethod
def uploadAssignmentMd5(username, courseId, assignmentId, md5Sum):
    strout = websutil.OutputString()
    #  Save file in a temp
    (fd, tmpname) = tempfile.mkstemp('.txt')
    with open(tmpname, 'wb', 10000) as f:
        f.write(md5Sum)
    os.close(fd)

    # Call submit.py
    ## Redirect stdout to catch logging messages from submit
    strout = websutil.OutputString()
    sys.stdout = strout
    try:
        submit.submit(tmpname, assignmentId, username, courseId)
    except submit.SubmittedTooSoonError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
                           'errorMessage':"Tema trimisa prea curand",
                           'errorTrace':strout.get()})

    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
                           'errorMessage':"",
                           'errorTrace':strout.get()})

    return json.dumps({'status':True,
                       'dumpLog':strout.get()})



########## @ServiceMethod
def beginEvaluation(username, courseId, assignmentId, archiveFileName):
    strout = websutil.OutputString()
    archiveValidationResult = websutil.validate_md5_submission(courseId, assignmentId, username, archiveFileName)
    if not(archiveValidationResult == "ok"):
        return json.dumps({'status':False, 'error':archiveValidationResult});
    # Call submit.py
    ## Redirect stdout to catch logging messages from submit
    strout = websutil.OutputString()
    sys.stdout = strout
    try:
        submit.evaluate_large_submission(archiveFileName, assignmentId, username, courseId)
    except submit.SubmittedTooSoonError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"Tema trimisa prea curand",
            'errorTrace':strout.get()})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
    return json.dumps({'status':True,
                       'dumpLog':strout.get()})


########## @ServiceMethod
def getResults(username, courseId, assignmentId):
    return getUserResults(courseId, assignmentId, username)

def getUserResults(courseId, assignmentId, username):
    strout = websutil.OutputString()
    try:
        vmcfg = config.CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    submission_dir = vmpaths.dir_cur_submission_root(assignmentId, username)
    r_path = paths.dir_submission_results(submission_dir)

    strout = websutil.OutputString()
    try:
        result_files = []
        if os.path.isdir(r_path):
            # XXX should we narrow scope on user & assignment?
            # TODO: add a routine to update user+asignment+course grade only
            #update_db.update_grades(courseId)
            for fname in os.listdir(r_path):
                # skill all files not ending in '.vmr'
                if not fname.endswith('.vmr'):
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
                        result_files.append({fname  : (f.read(MAX_VMR_FILE_SIZE) + overflow_msg) })

        if len(result_files) == 0:
            msg = "In the meantime have a fortune cookie"
            result_files = [ {'fortune.vmr' :  msg } ]
            result_files.append({'queue-contents.vmr' :  '' })
        result_files.append({'late-submission.vmr' :
                             websutil.submission_upload_info(courseId, username, assignmentId)})
        result_files = websutil.sortResultFiles(result_files)
        return json.dumps(result_files)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})


######### @ServiceMethod
def getCourses():
    course_arr = []
    strout = websutil.OutputString()
    try:
        clist = CourseList()
        for course_id in clist.course_names():
            course_cfg_fname = clist.course_config(course_id)
            course_cfg = CourseConfig(course_cfg_fname)
            course_title = course_cfg.course_name()
            course_arr.append({'id' : course_id,
                               'title' : course_title})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
             'errorMessage':"",
             'errorTrace':strout.get()})
    return json.dumps(course_arr)


######### @ServiceMethod
def getAssignments(courseId):
    strout = websutil.OutputString()
    try:
        vmcfg = config.CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
    assignments = vmcfg.assignments()
    sorted_assg = sorted(assignments, lambda x, y: int(assignments.get(x, "OrderNumber")) -
                                                   int(assignments.get(y, "OrderNumber")))
    ass_arr = []

    for key in sorted_assg:
        a = {}
        a['assignmentId'] = key
        a['assignmentTitle'] = assignments.get(key, "AssignmentTitle")
        a['assignmentStorage'] = assignments.getd(key, "AssignmentStorage", "")
        if a['assignmentStorage'].lower() == "large":
            a['assignmentStorageHost'] = assignments.get(key, "AssignmentStorageHost")
            a['assignmentStorageBasepath'] = assignments.storage_basepath(key, username)
        a['deadline'] = assignments.get(key, "Deadline")
        a['statementLink'] = assignments.get(key, "StatementLink")
        ass_arr.append(a)
    return json.dumps(ass_arr)

######### @ServiceMethod
def getUploadedMd5(username, courseId, assignmentId):
    """ Returns the md5 file for the current user"""
    # Get username session variable
    strout = websutil.OutputString()
    return getUserUploadedMd5(courseId, assignmentId, username)



def getUserUploadedMd5(courseId, assignmentId, username):
    """Get the current MD5 sum submitted for a given username on a given assignment"""
    strout = websutil.OutputString()
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

    strout = websutil.OutputString()

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


######### @ServiceMethod
def getStorageDirContents(username, courseId, assignmentId):
    return getUserStorageDirContents(courseId, assignmentId, username)



def getUserStorageDirContents(courseId, assignmentId, username):
    strout = websutil.OutputString()
    try:
        result = websutil.get_storagedir_contents(courseId, assignmentId, username)
        return result
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})


def getAllGrades(courseId):
    """Returns a table with all the grades of all students for a given course"""
    try:
        update_db.update_grades(courseId)
        vmcfg = CourseConfig(CourseList().course_config(courseId))
        vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
        db_conn = sqlite3.connect(vmpaths.db_file())
        assignments = vmcfg.assignments()
        sorted_assg = sorted(assignments, lambda x, y: int(assignments.get(x, "OrderNumber")) -
                                                       int(assignments.get(y, "OrderNumber")))

        grades = {}
        try:
            db_cursor = db_conn.cursor()
            db_cursor.execute(
                'SELECT users.name, assignments.name, grades.grade '
                'FROM users, assignments, grades '
                'WHERE 1 '
                'AND users.id = grades.user_id '
                'AND assignments.id = grades.assignment_id')
            for row in db_cursor:
                user, assignment, grade = row
                grades.setdefault(user, {})[assignment] = grade
            db_cursor.close()
        finally:
            db_conn.close()

        ret = []
        for user in sorted(grades.keys()):
            ret.append({'studentName' : user,
                        'studentId'   : user,
                        'results'     : grades.get(user)})
        return json.dumps(ret)
    except:
        strout = websutil.OutputString()
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})



######### @ServiceMethod
def login(username, password):
    time.sleep(1)
    strout = websutil.OutputString()
    try:
        user = websutil.get_user(username, password)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
    return json.dumps({'status':True, 'username':user,
            'info':'Succesfully logged in'})


######### @ServiceMethod
def logout():
    return json.dumps({'info':'You logged out'})



import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

server = SimpleXMLRPCServer(("localhost", 9090))
print "Listening on port 9090..."
server.register_function(getCourses)
server.register_function(getAssignments)
server.register_function(getAllGrades)
server.serve_forever()
