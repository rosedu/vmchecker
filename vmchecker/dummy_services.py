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


########## @ServiceMethod
def uploadAssignment(username, courseId, assignmentId, archiveFile):
    return json.dumps({'status':True,
                       'dumpLog':True})

########## @ServiceMethod
def uploadAssignmentMd5(username, courseId, assignmentId, md5Sum):
    return json.dumps({'status':True,
                       'dumpLog':True})



########## @ServiceMethod
def beginEvaluation(username, courseId, assignmentId, archiveFileName):
    return json.dumps({'status':True,
                       'dumpLog':True})


########## @ServiceMethod
def getResults(username, courseId, assignmentId):
    return json.dumps({'status':True,
                       'dumpLog':True})

def getUserResults(courseId, assignmentId, username):
    return json.dumps({'status':True,
                       'dumpLog':True})


######### @ServiceMethod
def getCourses():
    return json.dumps([{"id": "POO", "title": "Programare Orientata pe Obiecte (CB)"}, {"id": "PP", "title": "Paradigme de Programare"}, {"id": "CPL", "title": "Compilatoare"}, {"id": "PA", "title": "Proiectarea algoritmilor"}, {"id": "PC", "title": "Programarea Calculatoarelor (CA)"}, {"id": "USO", "title": "Utilizarea sistemelor de operare"}, {"id": "MN", "title": "Metode Numerice"}, {"id": "AC", "title": "Arhitectura Calculatoarelor"}, {"id": "CDL", "title": "CDL"}, {"id": "IA", "title": "Inteligenta Artificiala"}, {"id": "SO2", "title": "Sisteme de operare 2"}, {"id": "SO", "title": "Sisteme de operare"}, {"id": "RL", "title": "Retele locale"}, {"id": "CS4HS", "title": "CS4HS"}, {"id": "SD", "title": "Structuri de Date (CA)"}])


######### @ServiceMethod
def getAssignments(courseId):
    if courseId == "POO":
      return json.dumps([{"assignmentId": "tema1", "assignmentTitle": "Document retrieval", "deadline": "2012.11.06 23:59:00", "statementLink": "http://cursuri.cs.pub.ro/~poo/wiki/index.php/Tema1", "assignmentStorage": "normal"}, {"assignmentId": "tema2", "assignmentTitle": "Arbore genealogic", "deadline": "2012.11.30 23:59:00", "statementLink": "http://cursuri.cs.pub.ro/~poo/wiki/index.php/Tema2", "assignmentStorage": "normal"}, {"assignmentId": "tema3", "assignmentTitle": "Arbori de parsare", "deadline": "2013.01.13 23:59:00", "statementLink": "http://cursuri.cs.pub.ro/~poo/wiki/index.php/Tema3", "assignmentStorage": "normal"}, {"assignmentId": "tema4", "assignmentTitle": "Tabele de dispersie generice", "deadline": "2013.01.27 23:59:00", "statementLink": "http://cursuri.cs.pub.ro/~poo/wiki/index.php/Tema4", "assignmentStorage": "normal"}])
    if courseId == "PP":
      return json.dumps([{"assignmentId": "scheme", "assignmentTitle": "Scheme: Limbaj de interogare", "deadline": "2013.04.07 23:59:00", "statementLink": "http://elf.cs.pub.ro/pp/teme13/scheme-interogare", "assignmentStorage": "normal"}, {"assignmentId": "haskell", "assignmentTitle": "Haskell: Expresii regulate", "deadline": "2013.04.29 23:59:00", "statementLink": "http://elf.cs.pub.ro/pp/teme13/haskell-regexp", "assignmentStorage": "normal"}, {"assignmentId": "prolog", "assignmentTitle": "Prolog: X si 0 Cuantic", "deadline": "2013.05.29 23:59:00", "statementLink": "http://elf.cs.pub.ro/pp/teme13/prolog-qttt", "assignmentStorage": "normal"}, {"assignmentId": "clips", "assignmentTitle": "CLIPS : Phutball", "deadline": "2013.05.30 07:59:00", "statementLink": "http://elf.cs.pub.ro/pp/teme13/phutball", "assignmentStorage": "normal"}])
    return json.dumps([])

######### @ServiceMethod
def getUploadedMd5(username, courseId, assignmentId):
    return json.dumps({'status':True,
                       'dumpLog':True})



def getUserUploadedMd5(courseId, assignmentId, username):
    return json.dumps({'status':True,
                       'dumpLog':True})


######### @ServiceMethod
def getStorageDirContents(username, courseId, assignmentId):
    return json.dumps({'status':True,
                       'dumpLog':True})



def getUserStorageDirContents(courseId, assignmentId, username):
    return json.dumps({'status':True,
                       'dumpLog':True})


def getAllGrades(courseId):
    print courseId
    return json.dumps({'status':True,
                       'dumpLog':True})



######### @ServiceMethod
def login(username, password):
    return json.dumps({'status':True,
                       'dumpLog':True})


######### @ServiceMethod
def logout():
    return json.dumps({'status':True,
                       'dumpLog':True})

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

server = SimpleXMLRPCServer(("localhost", 9090))
print "Listening on port 8000..."
server.register_function(getCourses)
server.register_function(getAssignments)
server.serve_forever()