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
import subprocess
import time
import traceback

import ConfigParser
from mod_python import Cookie, apache, Session

from vmchecker.courselist import CourseList
from vmchecker import submit, config


# define ERROR_MESSAGES
ERR_ACCESS_DENIED = "Access denied."
ERR_FILE_NOT_UPLOADED = "File not uploaded."
ERR_EXCEPTION = "An exception occured on our server. Please notify the administrators."


AUTH_DB = [{'username' : 'vmchecker',
           'password' : 'vmchecker'}]

class OutputString():
	def __init__(self):
		self.st = ""

	def write(self, st):
		self.st += st
	
	def get(self):
		return self.st 


def get_user(credentials):
	#XXX : Cu LDAP
	for user in AUTH_DB:
		if (user['username'] == credentials['username']) and \
		   (user['password'] == credentials['password']):
			return user
	return None


# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
	while True:
		chunk = f.read(chunk_size)
		if not chunk: 
			break
		yield chunk


########## @ServiceMethod
def uploadAssignment(req, courseid, assignmentid, archivefile):
	""" Saves a temp file of the uploaded archive and calls
        vmchecker.submit.submit method to put the homework in
		the testing queue"""
	
	# Check permission
	s = Session.Session(req)
	if s.is_new():
		s.invalidate()
		return json.dumps({"error":ERR_ACCESS_DENIED})

	s.load()
	try:
		username = s['username']
	except:
		return json.dumps({"error":ERR_EXCEPTION + ": " + 
						"Could not fetch the username session variable."})  	
	
	# Reset the timeout
	s.save()

	# Get the archive name
	fileitem = req.form['archivefile']

	# Test if the file was uploaded
	if fileitem.filename == None:
		return  json.dumps({'error':ERR_FILE_NOT_UPLOADED})

	#  Save file in a temp
	fd, tmpname = tempfile.mkstemp('.zip')
	f = open(tmpname, 'wb', 10000)
    ## Read the file in chunks
	for chunk in fbuffer(fileitem.file):
		f.write(chunk)
	f.close()

	# Call submit.py
	## Redirect stdout
	strout = OutputString()
	sys.stdout = strout
	
	try:
		status = submit.submit(tmpname, assignmentid, 
							username, courseid)
	except:
		traceback.print_exc(file = strout)
		return json.dumps({'error':ERR_EXCEPTION + " : " + strout.get()})
	
	return json.dumps({'status':status,
            'dumpLog':strout.get()}) 


########## @ServiceMethod
def getResults(req, courseid, assignmentid):
	""" Returns the result for the current user"""

	# Check permission 	
	s = Session.Session(req)
	if s.is_new():
		s.invalidate()
		return json.dumps({"error":ERR_ACCESS_DENIED})

	# Get username session variable
	s.load()
	try:
		username = s['username']
	except:
		return json.dumps({"error":ERR_EXCEPTION + ": " + \
					"Could not fetch the username session variable."})  	

	strout = OutputString()
	try:
		vmcfg = config.VmcheckerConfig(CourseList().course_config(courseid))
	except:
		traceback.print_exc(file = strout)
		return json.dumps({'error':ERR_EXCEPTION + " : " + strout.get()})
				
	r_path =  vmcfg.repository_path() + "/" + assignmentid + \
										"/" + username + "/results/"

	# Reset the timeout
	s.save()

	if not os.path.isdir(r_path):
		#TODO fortune
		#TODO cand se updateaza baza de date?
		return json.dumps({'resultLog':'The results are not ready.'});
	else:
		resultlog = ""
		for fname in os.listdir(r_path):
			f_path = os.path.join(r_path, fname)
			if os.path.isfile(f_path):
				f = open(f_path, "r")
				resultlog += "===== " + fname + " =====\n"
				resultlog += f.read()
		return json.dumps({'resultlog':resultlog})


######### @ServiceMethod
def getCourses(req):
	""" Returns a JSON object containing the list of available courses """

	s = Session.Session(req)
	if s.is_new():
		s.invalidate()
		return json.dumps({"error":ERR_ACCESS_DENIED})

	# Reset the timeout
	s.save()

	strout = OutputString()
	try:
		clist = CourseList()
	except:
		traceback.print_exc(file = strout)
		return json.dumps({'error':ERR_EXCEPTION + " : " + strout.get()})
				
	course_arr = []
	for course_id in clist.course_names():
		course_arr.append({'id' : course_id,
			'title' : course_id}) # XXX: TODO: get a long name
	return json.dumps(course_arr)


######### @ServiceMethod
def getAssignments(req, courseid):
	""" Returns the list of assignments for a given course """

	s = Session.Session(req)
	if s.is_new():
		s.invalidate()
		return json.dumps({"error":ERR_ACCESS_DENIED})

	# Reset the timeout
	s.save()

	strout = OutputString()
	try:
		vmcfg = config.VmcheckerConfig(CourseList().course_config(courseid))
	except:
		traceback.print_exc(file = strout)
		return json.dumps({'error':ERR_EXCEPTION + " : " + strout.get()})

	assignments = vmcfg.assignments()
	ass_arr = []

	for key in assignments.__assignments:
		a = {}
		a['assignmentId'] = key
		a['assignmentTitle'] = assignments.get(key, "assignmentTitle")
		a['deadline'] = assignments.get(key, "deadline")
		ass_arr.append(a)
	return json.dumps(ass_arr)


######### @ServiceMethod
def login(req, username, password):
    s = Session.Session(req)

    if not s.is_new():
    	return json.dumps({'status':'true', 'username':username,
									'info':'Already logged in'})
    
    user = get_user({'username' : username, 'password' : password})
    if user is None:
        s.invalidate()
        return json.dumps({'status':'false', 'username':None, 
									'info':'Invalid username/password'})

    s["username"] = username
    s.save()
    return json.dumps({'status':'true', 'username':username,
									'info':'Succesfully logged in'})


######### @ServiceMethod
def logout(req):
    s = Session.Session(req)
    s.invalidate()

