#! /usr/bin/env python2.5

import misc
import os
import remote_check
import sys
import subprocess
import time

def revstrcmp(x, y):
    if x > y:
        return -1
    if x == y:
        return 0
    return 1

#globals
root = misc.vmchecker_root()
back = root + "/back"

def hwdir(hw):
    return back + "/" + hw

def main():
    argc = len(sys.argv)
    if argc == 1:
        check_all()
    elif argc == 2:
        try:
            check_hw_no(sys.argv[1])
        except OSError:
            print("Calea catre tema " + sys.argv[1] + " este invalida.")
            print("Verifica daca exista " + hwdir(sys.argv[1]))
    elif argc == 3:
        check_hw_student(sys.argv[1], sys.argv[2])

def check_all():
    for hw in os.listdir(back):
        check_hw_no(hw)

def check_hw_no(hw):
    print ("hw: " + hw)
    for name in os.listdir(hwdir(hw)):
        check_hw_student(hw, name)

def check_hw_student(hw, name):
    print ("name: " + name)
    namedir = hwdir(hw) + "/" + name
    dates = os.listdir(namedir)
    dates.sort(revstrcmp)
    for i in range(0, len(dates)):
        print dates[i]
        for date in dates:
            datedir = namedir + "/" + date
            inifile = datedir + "/" + date + " " + name + " " + hw + ".ini"

            try:
                os.stat(inifile)
            except OSError:
                continue
            print ("\t latest date of upload: " + date)
            print ("\t inifile: " + inifile)
            remote_check = os.path.join(os.path.dirname(sys.argv[0]), 
                                        'remote_check.py')
            return_code = 0
            try:
                return_code = subprocess.call([remote_check, inifile])
                    #print "\t remote_check" + inifile
            except OSError, e:
                print >> sys.stderr, 'Can\'t call %s (%s)' % (remote_check, str(e))
                
                if return_code != 0:
                    print >> sys.stderr, '%s failed' % remote_check
                    sys.exit(1)
                    
                break


if __name__ == "__main__":
    main()
