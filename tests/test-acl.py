#!/usr/bin/env python

from vmchecker.config import AclConfig

def main():
    acl = AclConfig()
    print "users :", acl.users()
    print "groups:", acl.groups()

if __name__ == "__main__":
    main()
