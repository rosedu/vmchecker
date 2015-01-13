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

from mod_python import Session

from vmchecker.courselist import CourseList
from vmchecker.config import CourseConfig
from vmchecker import submit, config, websutil, update_db, paths, submissions
from vmchecker.config import DATE_FORMAT

########## @ServiceMethod
def uploadedFile(req, courseId, assignmentId, tmpname, locale=websutil.DEFAULT_LOCALE):
    """ Saves a temp file of the uploaded archive and calls
        vmchecker.submit.submit method to put the homework in
        the testing queue"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)
    # TODO a better check is needed for tmpname
    websutil.sanityCheckDotDot(tmpname)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})     
    
    # Reset the timeout
    s.save()

    # Call submit.py
    ## Redirect stdout to catch logging messages from submit
    strout = websutil.OutputString()
    sys.stdout = strout
    try:
        submit.submit(tmpname, assignmentId, username, courseId)
        update_db.update_grades(courseId, user=username, assignment=assignmentId)
    except submit.SubmittedTooSoonError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("Sent too fast"),
            'errorTrace':strout.get()})
    except submit.SubmittedTooLateError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("The assignment was submitted too late"),
            'errorTrace':strout.get()})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
    
    return json.dumps({'status':True,
                       'dumpLog':strout.get()})

########## @ServiceMethod
def uploadAssignment(req, courseId, assignmentId, archiveFile, locale=websutil.DEFAULT_LOCALE):
    """ Saves a temp file of the uploaded archive and calls
        vmchecker.submit.submit method to put the homework in
        the testing queue"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))
	
    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})  	
	
    # Reset the timeout
    s.save()

    if archiveFile.filename == None:
        return  json.dumps({'errorType':websutil.ERR_OTHER,
                    'errorMessage':_("File not uploaded."),
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
        update_db.update_grades(courseId, user=username, assignment=assignmentId)
    except submit.SubmittedTooSoonError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("The assignment was submitted too soon"),
            'errorTrace':strout.get()})
    except submit.SubmittedTooLateError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("The assignment was submitted too late"),
            'errorTrace':strout.get()})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
	
    return json.dumps({'status':True,
                       'dumpLog':strout.get(),
                       'file': tmpname}) 

########## @ServiceMethod
def uploadAssignmentMd5(req, courseId, assignmentId, md5Sum, locale=websutil.DEFAULT_LOCALE):
    """ Saves a temp file of the uploaded archive and calls
        vmchecker.submit.submit method to put the homework in
        the testing queue"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                           'errorMessage':"",
                           'errorTrace':""})

    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
                           'errorMessage':"",
                           'errorTrace':strout.get()})

    # Reset the timeout
    s.save()

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
        update_db.update_grades(courseId, user=username, assignment=assignmentId)
    except submit.SubmittedTooSoonError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
                           'errorMessage':_("The assignment was submitted too soon"),
                           'errorTrace':strout.get()})
    except submit.SubmittedTooLateError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("The assignment was submitted too late"),
            'errorTrace':strout.get()})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
                           'errorMessage':"",
                           'errorTrace':strout.get()})

    return json.dumps({'status':True,
                       'dumpLog':strout.get()})



########## @ServiceMethod
def beginEvaluation(req, courseId, assignmentId, archiveFileName, locale=websutil.DEFAULT_LOCALE):
    """ Saves a temp file of the uploaded archive and calls
        vmchecker.submit.submit method to put the homework in
        the testing queue"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)
    # TODO archiveFileName
    websutil.sanityCheckDotDot(archiveFileName)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})

    # Reset the timeout
    s.save()

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
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("The assignment was submitted too soon"),
            'errorTrace':strout.get()})
    except submit.SubmittedTooLateError:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':_("The assignment was submitted too late"),
            'errorTrace':strout.get()})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})

    # Reset the timeout
    s.save()

    return json.dumps({'status':True,
                       'dumpLog':strout.get()})



########## @ServiceMethod
def getResults(req, courseId, assignmentId, locale=websutil.DEFAULT_LOCALE):
    """ Returns the result for the current user"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    # Get username session variable
    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})
    # Reset the timeout
    s.save()
    return websutil.getUserResultsHelper(req, courseId, assignmentId, username)

########## @ServiceMethod
def getUserResults(req, courseId, assignmentId, username, locale=websutil.DEFAULT_LOCALE):
    """Get the results for a given username"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)
    websutil.sanityCheckUsername(username)

    req.content_type = 'text/html'

    # Check permission
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    # Reset the timeout
    s.save()
    return websutil.getUserResultsHelper(req, courseId, assignmentId, username)

######### @ServiceMethod
def getCourses(req):
    """ Returns a JSON object containing the list of available courses """

    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})
		
    # Reset the timeout
    s.save()

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
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
             'errorMessage':"",
             'errorTrace':strout.get()})  	
				
    return json.dumps(course_arr)


######### @ServiceMethod
def getAssignments(req, courseId, locale=websutil.DEFAULT_LOCALE):
    """ Returns the list of assignments for a given course """

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckCourseId(courseId)

    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"Session is new",
                'errorTrace':""})

    # Get username session variable
    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "Unable to load session",
                           'errorTrace' : strout.get()})
    # Reset the timeout
    s.save()

    try:
        vmcfg = config.CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"Unable to load course config",
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
def getUploadedMd5(req, courseId, assignmentId, locale=websutil.DEFAULT_LOCALE):
    """ Returns the md5 file for the current user"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    # Get username session variable
    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})
    # Reset the timeout
    s.save()
    return websutil.getUserUploadedMd5(req, courseId, assignmentId, username)


######### @ServiceMethod
def getStorageDirContents(req, courseId, assignmentId, locale=websutil.DEFAULT_LOCALE):
    """ Returns the file list from the storage host for the current user"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                           'errorMessage':"",
                           'errorTrace':""})

    # Get username session variable
    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})
    # Reset the timeout
    s.save()
    return websutil.getUserStorageDirContents(req, courseId, assignmentId, username)


######### @ServiceMethod
def getAllGrades(req, courseId, locale=websutil.DEFAULT_LOCALE):
    """Returns a table with all the grades of all students for a given course"""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckCourseId(courseId)

    req.content_type = 'text/html'

    # Check permission
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    # Reset the timeout
    s.save()

    try:
        # XXX: DON'T DO THIS: performance degrades very much!
        #update_db.update_grades(courseId)
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
                if not assignment in vmcfg.assignments():
                    continue
                if not vmcfg.assignments().show_grades_before_deadline(assignment):
                    deadline = time.strptime(vmcfg.assignments().get(assignment, 'Deadline'), DATE_FORMAT)
                    deadtime = time.mktime(deadline)
                    if time.time() < deadtime:
                        continue
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
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})


######### @ServiceMethod
def login(req, username, password, locale=websutil.DEFAULT_LOCALE):

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    #### BIG FAT WARNING: ####
    # If you ever try to use Vmchecker on a UserDir-type environment
    # (i.e., ~/public_html), **DON'T**.
    # It appears that mod_python tries to set a cookie with the path
    # determined by DocumentRoot. This means that the path itself
    # gets mangled and the browser doesn't send the cookie back.
    #
    # This results in the app never logging in, simply coming back
    # to the login screen.
    #
    # If you have access to the browser config, you can try and
    # manually set 'ApplicationPath' to '/' in order to circumvent
    # this.
    #### / BIG FAT WARNING ####

    req.content_type = 'text/html'
    # don't permit brute force password guessing:
    time.sleep(1)
    s = Session.Session(req)

    websutil.sanityCheckUsername(username)

    if not s.is_new():
	#TODO take the username from session
        return json.dumps({'status':True, 'username':username,
            'info':'Already logged in'})

    strout = websutil.OutputString()
    try:
        user = websutil.get_user(username, password)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':websutil.ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})  	

    if user is None:
        s.invalidate()
        return json.dumps({'status':False, 'username':"", 
            'info':_('Invalid username/password')})

    s["username"] = username.lower()
    s.save()
    return json.dumps({'status':True, 'username':user,
            'info':'Succesfully logged in'})

######### @ServiceMethod
def autologin(req, username):
    return json.dumps({})
    req.content_type = 'text/html'
    # don't permit brute force password guessing:
    time.sleep(1)

    websutil.sanityCheckUsername(username)

    s = Session.Session(req)

    if not s.is_new():
	#TODO take the username from session
        return json.dumps({'status':True, 'username':username,
            'info':'Already logged in'})

    if not req.connection.remote_ip == '127.0.0.1':
        s.invalidate()
        return json.dumps({'status':False, 'username':"", 
            'info':req.connection.remote_ip})

    s["username"] = username.lower()
    s.save()
    return json.dumps({'status':True, 'username':username,
            'info':'Success!'})


######### @ServiceMethod
def logout(req):
    req.content_type = 'text/html'
    s = Session.Session(req)
    s.invalidate()
    return json.dumps({'info':'You logged out'})


