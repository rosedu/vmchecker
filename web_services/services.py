import os
import sys
import subprocess
import json

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

########## @ServiceMethod
def uploadAssignment(req, courseid, assignmentid, username, archivefile):

   ### 1) Save file in a temp
   #TODO  generate a unique temp name (username is unique?) + chmod + delete   
   fileitem = req.form['archivefile']
   # Test if the file was uploaded
   if fileitem.filename:
      # strip leading path from file name 
      fname = os.path.basename(fileitem.filename)
      # build absolute path to files directory
      dir_path = os.path.join(os.path.dirname(req.filename), 'files')
      file_path = os.path.join(dir_path, fname) 	
      f = open(file_path, 'wb', 10000)
      # Read the file in chunks
      for chunk in fbuffer(fileitem.file):
         f.write(chunk)
      f.close()

      ### 2) Call submit.py
      #TODO de-hardcode	
      hard_path = '/home/szekeres/Desktop/vmchecker/bin/submit.py'
      process = subprocess.Popen(['python', hard_path, assignmentid, username],
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

########## @ServiceMethod
def getResults(req, courseid, assignmentid, username):



######### @ServiceMethod
def getCourses(req):

######### @ServiceMethod
def getAssignments(req, courseid):

######### @ServiceMethod
def login(req, username, password): 
