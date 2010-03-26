#!/usr/bin/env python

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
import tempfile
import traceback
import subprocess

from mod_python import Session

from vmchecker.courselist import CourseList
from vmchecker.config import CourseConfig
from vmchecker import submit, config, websutil, update_db, paths

# define ERROR_MESSAGES
ERR_AUTH = 1
ERR_EXCEPTION = 2 
ERR_OTHER = 3



########## @ServiceMethod
def uploadAssignment(req, courseId, assignmentId, archiveFile):
    """ Saves a temp file of the uploaded archive and calls
        vmchecker.submit.submit method to put the homework in
        the testing queue"""
	
    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})  	
	
    # Reset the timeout
    s.save()

    if archiveFile.filename == None:
        return  json.dumps({'errorType':ERR_OTHER,
                    'errorMessage':"File not uploaded.",
                    'errorTrace':""})

    #  Save file in a temp
    fd, tmpname = tempfile.mkstemp('.zip')
    f = open(tmpname, 'wb', 10000)
    ## Read the file in chunks
    for chunk in websutil.fbuffer(archiveFile.file):
        f.write(chunk)
    f.close()

    # Call submit.py
    ## Redirect stdout to catch logging messages from submit
    strout = websutil.OutputString()
    sys.stdout = strout
    try:
        submit.submit(tmpname, assignmentId, username, courseId)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
	
    return json.dumps({'status':True,
                       'dumpLog':strout.get()}) 


########## @ServiceMethod
def getResults(req, courseId, assignmentId):
    """ Returns the result for the current user"""

    # Check permission
    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})

    # Get username session variable
    strout = websutil.OutputString()
    try:
        s.load()
        username = s['username']
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    strout = websutil.OutputString()
    try:
        vmcfg = config.CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})

    vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    submission_dir = vmpaths.dir_submission_root(assignmentId, username)
    r_path = paths.dir_submission_results(submission_dir)

    # Reset the timeout
    s.save()

    strout = websutil.OutputString()
    try:
        result_files = {}
        if not os.path.isdir(r_path):
            process = subprocess.Popen('/usr/games/fortune',
                                       shell=False,
                                       stdout=subprocess.PIPE)
            msg = "In the meantime have a fortune cookie: <blockquote>"
            msg += process.communicate()[0] + "</blockquote>"
            result_files['Your results are not ready yet'] = msg
        else:
            #XXX: move this update somewhere else?
            update_db.update_all(courseId)
            for fname in os.listdir(r_path):
                f_path = os.path.join(r_path, fname)
                if os.path.isfile(f_path):
                    with open(f_path, 'r') as f:
                        result_files[fname] = f.read()
        return json.dumps({'resultFiles':result_files})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType' : ERR_EXCEPTION,
                           'errorMessage' : "",
                           'errorTrace' : strout.get()})


######### @ServiceMethod
def getCourses(req):
    """ Returns a JSON object containing the list of available courses """

    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':ERR_AUTH,
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
        return json.dumps({'errorType':ERR_EXCEPTION,
             'errorMessage':"",
             'errorTrace':strout.get()})  	
				
    return json.dumps(course_arr)


######### @ServiceMethod
def getAssignments(req, courseId): 
    """ Returns the list of assignments for a given course """

    req.content_type = 'text/html'
    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return json.dumps({'errorType':ERR_AUTH,
                'errorMessage':"",
                'errorTrace':""})
		
    # Reset the timeout
    s.save()

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
        a['deadline'] = assignments.get(key, "Deadline")
        a['statementLink'] = assignments.get(key, 'StatementLink')
        ass_arr.append(a)
    return json.dumps(ass_arr)


######### @ServiceMethod
def login(req, username, password):
    req.content_type = 'text/html'
    s = Session.Session(req)

    if not s.is_new():
	#TODO take the username from session
        return json.dumps({'status':True, 'username':username,
            'info':'Already logged in'})

    strout = websutil.OutputString()
    try:
        user = websutil.get_user({'username' : username, 'password' : password})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})  	

    if user is None:
        s.invalidate()
        return json.dumps({'status':False, 'username':"", 
            'info':'Invalid username/password'})

    s["username"] = username
    s.save()
    return json.dumps({'status':True, 'username':user,
            'info':'Succesfully logged in'})


######### @ServiceMethod
def logout(req):
    req.content_type = 'text/html'
    s = Session.Session(req)
    s.invalidate()
    return json.dumps({'info':'You logged out'})
