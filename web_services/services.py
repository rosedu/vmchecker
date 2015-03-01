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
import tempfile
import traceback
import subprocess
import datetime

from mod_python import Session, Cookie

from vmchecker.courselist import CourseList
from vmchecker.config import StorerCourseConfig
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
    sys.stdout = strout
    (hasTeam, account) = websutil.getAssignmentAccountName(courseId, assignmentId, username, strout)
    try:
        if hasTeam:
            submit.submit(tmpname, assignmentId, account, courseId, user = username)
        else:
            submit.submit(tmpname, assignmentId, account, courseId)
        update_db.update_grades(courseId, account, assignment = assignmentId)
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
    sys.stdout = strout
    (hasTeam, account) = websutil.getAssignmentAccountName(courseId, assignmentId, username, strout)
    try:
        if hasTeam:
            submit.submit(tmpname, assignmentId, account, courseId, user = username)
        else:
            submit.submit(tmpname, assignmentId, account, courseId)
        update_db.update_grades(courseId, account, assignment = assignmentId)
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
    sys.stdout = strout
    (hasTeam, account) = websutil.getAssignmentAccountName(courseId, assignmentId, username, strout)
    try:
        if hasTeam:
            submit.submit(tmpname, assignmentId, account, courseId, user = username)
        else:
            submit.submit(tmpname, assignmentId, account, courseId)
        update_db.update_grades(courseId, account, assignment = assignmentId)
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

    (_, account) = websutil.getAssignmentAccountName(courseId, assignmentId, username, strout)
    archiveValidationResult = websutil.validate_md5_submission(courseId, assignmentId, account, archiveFileName)
    if not(archiveValidationResult[0]):
        return json.dumps({'status' : False, 'error' : archiveValidationResult[1]});

    # Call submit.py
    ## Redirect stdout to catch logging messages from submit
    sys.stdout = strout

    try:
        submit.evaluate_large_submission(archiveFileName, assignmentId, account, courseId)
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
def getTeamResults(req, courseId, assignmentId, teamname=None, locale=websutil.DEFAULT_LOCALE):
    """Get the results for a given team name.
       If the team name is empty, get the results of the current user's team."""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)
    if teamname != None:
        websutil.sanityCheckUsername(teamname)

    req.content_type = 'text/html'
    strout = websutil.OutputString()

    # Check permission
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    try:
        s.load()
        current_user = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    (hasTeam, current_team) = websutil.getAssignmentAccountName(courseId, assignmentId, current_user, strout)
    if teamname == None:
        if not hasTeam:
            # User is not part of any team for the assignment
            return json.dumps({'errorType' : websutil.ERR_OTHER,
                               'errorMessage' : "User is not part of any team for this assignment",
                               'errorTrace' : ""})
        teamname = current_team

    # Reset the timeout
    s.save()
    return websutil.getResultsHelper(courseId,
                                     assignmentId,
                                     current_user,
                                     strout,
                                     teamname = teamname,
                                     currentTeam = current_team)

########## @ServiceMethod
def getUserResults(req, courseId, assignmentId, username=None,
        locale=websutil.DEFAULT_LOCALE):
    """Get the individual results for a given username.
       If the username is empty, get the results of the current user."""

    websutil.install_i18n(websutil.sanityCheckLocale(locale))

    websutil.sanityCheckAssignmentId(assignmentId)
    websutil.sanityCheckCourseId(courseId)
    if username != None:
        websutil.sanityCheckUsername(username)

    req.content_type = 'text/html'
    strout = websutil.OutputString()

    # Check permission
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':websutil.ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    try:
        s.load()
        current_user = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    if username == None:
        username = current_user

    # Reset the timeout
    s.save()
    return websutil.getResultsHelper(courseId,
                                     assignmentId,
                                     current_user,
                                     strout,
                                     username = username)

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
            course_cfg = StorerCourseConfig(course_cfg_fname)
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

    return websutil.getAssignmentsHelper(courseId, username, strout)

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
    return websutil.getUserUploadedMd5Helper(courseId, assignmentId, username, strout)


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
    return websutil.getUserStorageDirContentsHelper(courseId, assignmentId, username, strout)


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

    return websutil.getAllGradesHelper(courseId, username, strout)

######### @ServiceMethod
def login(req, username, password, remember_me=False, locale=websutil.DEFAULT_LOCALE):

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

    strout = websutil.OutputString()

    if not s.is_new():
        try:
            s.load()
            username = s['username']
            fullname = s['fullname']
        except:
            traceback.print_exc(file = strout)
            return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                               'errorMessage' : "Getting user info from existing session failed",
                               'errorTrace' : strout.get()})

        return json.dumps({'status' : True,
                           'username' : username,
                           'fullname' : fullname,
                           'info' : 'Already logged in'})

    try:
        user = websutil.get_user(username, password)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : websutil.ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    if user is None:
        s.invalidate()
        return json.dumps({'status' : False,
                           'username' : "",
                           'fullname' : "",
                           'info':_('Invalid username/password')})

    # Use extended session timeout if requested
    if remember_me != False:
        c = s.make_cookie()
        expiration = datetime.datetime.now()
        expiration += datetime.timedelta(seconds = websutil.EXTENDED_SESSION_TIMEOUT)
        c.expires = expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

        req.headers_out.clear()
        Cookie.add_cookie(req, c)

        s.set_timeout(websutil.EXTENDED_SESSION_TIMEOUT)

    username = username.lower()
    s["username"] = username
    s["fullname"] = user
    s.save()
    return json.dumps({'status' : True,
                       'username' : username,
                       'fullname' : user,
                       'info' : 'Succesfully logged in'})

######### @ServiceMethod
def logout(req):
    req.content_type = 'text/html'
    s = Session.Session(req)
    s.invalidate()
    return json.dumps({'info':'You logged out'})


