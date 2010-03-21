#!/usr/bin/env python

from vmchecker.config import LdapConfig
import ldap

class OutputString():
    def __init__(self):
        self.st = ""

    def write(self, st):
        self.st += st
	
    def get(self):
        return self.st 

# using a LDAP server
def get_user(credentials):
    ldap_cfg = LdapConfig()
    con = ldap.initialize(ldap_cfg.server())
    con.simple_bind_s(ldap_cfg.bind_user(),
                        ldap_cfg.bind_pass())

    baseDN = ldap_cfg.root_search()
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None 
    searchFilter = 'uid=' + credentials['username'] 
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
        con.simple_bind_s(user_dn,
                          credentials['password'])
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

