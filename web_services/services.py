"""
   File: services.py
   Date: February 2010
  
   This script implements the VMChecker's Web Services.
   It is based on apache2 and mod_python.
"""

import os
import sys
import subprocess
import json
import tempfile
import ConfigParser
import time

from mod_python import Cookie, apache

#import config
#import vmcheckerpaths

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

########## @ServiceMethod
def uploadAssignment(req, courseid, assignmentid, username, archivefile):
   if Cookie.get_cookie(req, 'username'):
      ###  Save file in a temp  
      fileitem = req.form['archivefile']
      # Test if the file was uploaded
      if fileitem.filename:
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

      else:
         return  json.dumps({'status':None,
			   'dumpLog':'No file has been received'})
   else:
      return apache.HTTP_FORBIDDEN

########## @ServiceMethod
def getResults(req, courseid, assignmentid, username): 
   if Cookie.get_cookie(req, 'username'):
      #TODO xxx de-hardcode	
      #config.config_storer()
      #r_path = vmcheckerpaths.dir_results(courseid, assignmentid, username)
      r_path = "/home/szekeres/vmchecker/repo/"+courseid + "/" + assignmentid +"/" + username + "/results/"

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
   else:
      return apache.HTTP_FORBIDDEN

######### @ServiceMethod
def getCourses(req):
   if Cookie.get_cookie(req, 'username'):
      #TODO xxx Dupa ce termina Lucian
      return json.dumps([{'id':'so','title':'Sisteme de Operare'},
		      {'id':'pso','title':'Sisteme de Operare 2'},
                      {'id':'cpl','title':'Compilatoare'},
                      {'id':'pa','title':'Proiectarea Algoritmilor'}])
   else:
      return apache.HTTP_FORBIDDEN

######### @ServiceMethod
def getAssignments(req, courseid):
   if Cookie.get_cookie(req, 'username'):
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
         #'The configuration file doesn\'t exist'
	 return json.dumps(None) 	
   else:
      return apache.HTTP_FORBIDDEN

######### @ServiceMethod
def login(req, username, password):
   #TODO xxx
   if username == 'vmchecker' and password == 'vmchecker':
      cookie = Cookie.Cookie('username', username)
      cookie.expires = time.time() + 300
      Cookie.add_cookie(req, cookie)
      return apache.OK
   else:
      return apache.HTTP_FORBIDDEN
   
