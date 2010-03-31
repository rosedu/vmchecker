#!/usr/bin/env python

from __future__ import with_statement


import os
import ldap

from vmchecker import paths
from vmchecker.courselist import CourseList
from vmchecker.config import LdapConfig, CourseConfig

try:
    import simplejson as json
except ImportError:
    import json


class OutputString():
    def __init__(self):
        self.st = ""

    def write(self, st):
        self.st += st
	
    def get(self):
        return self.st 


def get_user(username, password):
    """Find the username for a user based on username/password.

    This searches LDAP or some file-based json files in the user's
    home directories.

    Returns the username on success.
    """

    # allthough a misconfigured user can block access to any course,
    # we preffer early LOUD errors to silently ignored ones.
    # Fail fast, fail lowdly!
    r = get_user_from_auth_files(username, password)
    if not r is None:
        return r
    return get_ldap_user(username, password)


def get_user_from_auth_files(username, password):
    """Search all courseses for auth_files and if we can login in any
    course, return the login from there"""
    for coursecfg_fname in CourseList().course_configs():
        vmpaths = paths.VmcheckerPaths(CourseConfig(coursecfg_fname).root_path())
        r = get_user_from_auth_file(vmpaths, username, password)
        if not r is None:
            return r
    return None



def get_user_from_auth_file(vmpaths, username, password):
    """Try to authenticate using one course's auth_file.

    Return the username on success.
    """
    if not os.path.exists(vmpaths.auth_file()):
        return None
    with open(vmpaths.auth_file()) as handle:
        auth_file_contents =  handle.read()
        auth_dic = json.loads(auth_file_contents)['auth']
    if auth_dic.has_key(username) and auth_dic[username] == password:
        return username
    return None


def get_ldap_user(username, password):
    """Try to authenticate using the global LDAP configuration file.

    Return the username on success.
    """
    ldap_cfg = LdapConfig()
    con = ldap.initialize(ldap_cfg.server())
    con.simple_bind_s(ldap_cfg.bind_user(),
                        ldap_cfg.bind_pass())

    baseDN = ldap_cfg.root_search()
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None 

    # XXX : Needs sanitation
    searchFilter = '(uid=' + username + ')'

    timeout = 0
    count = 0

    # find the user's dn
    result_id = con.search(baseDN, 
                        searchScope, 
                        searchFilter, 
                        retrieveAttributes)
    result_set = []
    while 1:
        result_type, result_data = con.result(result_id, timeout)
        if (result_data == []):
            break
        else:
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)

    if len(result_set) == 0:
        #no results
        return None

    if len(result_set) > 1:
        # too many results for the same uid
        raise

    user_dn, entry = result_set[0][0]	
    con.unbind_s()
    
    # check the password 
    try:  
        con = ldap.initialize(ldap_cfg.server())
        con.simple_bind_s(user_dn, password)
    except ldap.INVALID_CREDENTIALS:
        return None
    except:
        raise

    return entry['cn'][0]

  
# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
    while True:
        chunk = f.read(chunk_size)
        if not chunk: 
            break
        yield chunk


def _find_file(searched_file_name, rfiles):
    """Search for a filename in an array for {fname:fcontent} dicts"""
    for rfile in rfiles:
        if rfile.has_key(searched_file_name):
            return rfile
    return None


def sortResultFiles(rfiles):
    """Sort the vector of result files and change keys with human
    readable descriptions"""

    file_descriptions = [
        {'grade.vmr'            : 'Nota și observații'},
        {'vmchecker-stderr.vmr' : 'Erori vmchecker'},
        {'build-stdout.vmr'     : 'Compilarea temei și a testelor (stdout)'},
        {'build-stderr.vmr'     : 'Compilarea temei și a testelor (stderr)'},
        {'run-stdout.vmr'       : 'Execuția testelor (stdout)'},
        {'run-stderr.vmr'       : 'Execuția testelor (stderr)'},
        {'run-km.vmr'           : 'Mesaje kernel (netconsole)'},
        ]
    ret = []
    for f_des in file_descriptions:
        key = f_des.keys()[0] # there is only one key:value pair in each dict
        rfile = _find_file(key, rfiles)
        if rfile == None:
            ret.append({f_des.get(key) : 'Nu a fost găsit în vmchecker storer'})
        else:
            ret.append({f_des.get(key) : rfile.get(key)})
            rfiles.remove(rfile)
    ret += rfiles
    return ret
