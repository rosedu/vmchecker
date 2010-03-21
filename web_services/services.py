#!/usr/bin/env python

"""
This script implements the VMChecker's Web Services.
It's based on apache2 and mod_python.
"""


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
from vmchecker import submit, config, websutil, update_db

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
        status = submit.submit(tmpname, assignmentId, 
                   username, courseId)
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})
	
    return json.dumps({'status':status,
                       'dumpLog':strout.get()}) 


########## @ServiceMethod
def getResults(req, courseId, assignmentId):
    """ Returns the result for the current user"""

    # Check permission 	
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
        return json.dumps({'errorType':ERR_EXCEPTION,
                'errorMessage':"",
                'errorTrace':strout.get()})  	
		 	
    strout = websutil.OutputString()
    try:
        
        vmcfg = config.CourseConfig(CourseList().course_config(courseId))
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
            'errorMessage':"",
            'errorTrace':strout.get()})  	
						
    r_path =  vmcfg.repository_path() + "/" + assignmentId + \
            "/" + username + "/results/"

    # Reset the timeout
    s.save()

    strout = websutil.OutputString()
    try:
        if not os.path.isdir(r_path):
            process = subprocess.Popen('/usr/games/fortune', 
                             shell=False, 
                             stdout=subprocess.PIPE)
            resultlog = "<div align=center> Your results are not ready yet. <p> " + \
                        "In the meantime have a fortune: <p>" + \
                          process.communicate()[0] + "</div>" 
        else:
            #XXX: move this update somewhere else? 
            update_db.update_all(courseId)
            resultlog = ""
            for fname in os.listdir(r_path):
                f_path = os.path.join(r_path, fname)
                if os.path.isfile(f_path):
                    f = open(f_path, "r")
                    resultlog += "===== " + fname + " =====\n"
                    resultlog += f.read()
        return json.dumps({'resultlog':resultlog})
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
                 'errorMessage':"",
                 'errorTrace':strout.get()})  	                           


######### @ServiceMethod
def getCourses(req):
    """ Returns a JSON object containing the list of available courses """

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
        clist = CourseList()
    except:
        traceback.print_exc(file = strout)
        return json.dumps({'errorType':ERR_EXCEPTION,
             'errorMessage':"",
             'errorTrace':strout.get()})  	
				
    course_arr = []
    for course_id in clist.course_names():
        course_arr.append({'id' : course_id,
            'title' : course_id}) # XXX: TODO: get a long name
    return json.dumps(course_arr)


######### @ServiceMethod
def getAssignments(req, courseId): 
    """ Returns the list of assignments for a given course """

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
    ass_arr = []

    for key in assignments:
        a = {}
        a['assignmentId'] = key
        a['assignmentTitle'] = assignments.get(key, "AssignmentTitle")
        a['deadline'] = assignments.get(key, "Deadline")
        ass_arr.append(a)
    return json.dumps(ass_arr)


######### @ServiceMethod
def login(req, username, password):
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

    s["username"] = user
    s.save()
    return json.dumps({'status':True, 'username':user,
            'info':'Succesfully logged in'})


######### @ServiceMethod
def logout(req):
    s = Session.Session(req)
    s.invalidate()
    return json.dumps({'info':'You logged out'})
