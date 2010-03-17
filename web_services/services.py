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

import ConfigParser
from mod_python import Cookie, apache, Session

#import config
#import vmcheckerpaths

AUTH_DB = [{'username' : 'vmchecker',
           'password' : 'vmchecker'}]


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
        if not chunk: break
        yield chunk


########## @ServiceMethod
def uploadAssignment(req, courseid, assignmentid, username, archivefile):
    """ Saves a temp file of the uploaded archive and calls
        submit.py to put the homework in the testing queue"""

    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return apache.HTTP_FORBIDDEN

    # Reset the timeout
    s.save()

    fileitem = req.form['archivefile']

    # Test if the file was uploaded
    if fileitem.filename == None:
        return  json.dumps({'status':None,
            'dumpLog':'No file has been received'})

    ###  Save file in a temp
    fd, tmpname = tempfile.mkstemp('.zip')
    f = open(tmpname, 'wb', 10000)
    # Read the file in chunks
    for chunk in fbuffer(fileitem.file):
        f.write(chunk)
    f.close()

    ###  Call submit.py
    #TODO xxx de-harcode
    #config.config_storer()
    #s_path = os.path.join(vmcheckerpaths.dir_bin(),'submit.py')
    s_path = '/home/szekeres/Desktop/vmchecker/bin/submit.py'

    process = subprocess.Popen(['python', s_path, assignmentid,
            username, tmpname],
            shell=False,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE)

    dumpLog = process.communicate()[0]
    status = process.returncode

    return json.dumps({'status':status,
            'dumpLog':dumpLog})


########## @ServiceMethod
def getResults(req, courseid, assignmentid, username):
    """ Returns the result for the current user"""

    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return apache.HTTP_FORBIDDEN

    # Reset the timeout
    s.save()

    #TODO xxx de-hardcode
    #config.config_storer()
    #r_path = vmcheckerpaths.dir_results(courseid, assignmentid, username)
    r_path = "/home/szekeres/vmchecker/repo/" + courseid + \
            "/" + assignmentid +"/" + username + "/results/"

    if not os.path.isdir(r_path):
        #TODO fortune
        #TODO cand se updateaza baza de date?
        return json.dumps({'resultLog':'not yet'});
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
        return apache.HTTP_FORBIDDEN

    # Reset the timeout
    s.save()

    #TODO xxx Dupa ce termina Lucian
    return json.dumps([{'id':'so','title':'Sisteme de Operare'},
        {'id':'pso','title':'Sisteme de Operare 2'},
        {'id':'cpl','title':'Compilatoare'},
        {'id':'pa','title':'Proiectarea Algoritmilor'}])


######### @ServiceMethod
def getAssignments(req, courseid):
    """ Returns the list of assignments for a given course """

    s = Session.Session(req)
    if s.is_new():
        s.invalidate()
        return apache.HTTP_FORBIDDEN

    # Reset the timeout
    s.save()

    #TODO Nu stiu inca layoutul final al fisierelor de configurare - dupa ce termina Lucian
    #TODO xxx path to .vmcheckerrc for this courseid
    #config.config_storer()
    c_path = '/home/szekeres/storer.ini'
    parser = ConfigParser.RawConfigParser()
    assignments = []
    if parser.read(c_path):
        for section in parser.sections():
            s = section.split()
            if s[0] == 'assignment' and s[1] !=  'DEFAULT':
            #for each assignment section
                a = {}
                a['assignmentId'] = s[1]
                a['assignmentTitle'] = parser.get(section, 'Title')
                a['deadline'] = parser.get(section, 'Deadline')
                assignments.append(a)
        return json.dumps(assignments)
    else:
    #'The configuration file doesn't exist'
        return json.dumps(None)


######### @ServiceMethod
def login(req, username, password):
    s = Session.Session(req)
    if not s.is_new():
        return "Not supposed to be here, you're already logged in"

    user = get_user({'username' : username, 'password' : password})
    if user is None:
        s.invalidate()
        return "You're not from these places"

    s["username"] = username
    s.save()
    return "You are logged in"


######### @ServiceMethod
def logout(req):
    s = Session.Session(req)
    s.invalidate()
    return "You logged out"


