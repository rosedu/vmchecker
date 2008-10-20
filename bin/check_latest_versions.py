#! /usr/bin/env python2.5

import misc
import os
import remote_check
import sys
import subprocess
import time

def main():
    root = misc.vmchecker_root()
    back = root + "/back"
    for hw in os.listdir(back):
        print ("hw: " + hw)
        hwdir = back + "/" + hw
        for name in os.listdir(hwdir):
            print ("name: " + name)
            namedir = hwdir + "/" + name
            dates = os.listdir(namedir)
            dates.sort(lambda x, y: x < y)
            print dates
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
                    print ("")
                    #return_code = subprocess.call([remote_check, inifile])
                    #print "\t remote_check" + inifile
                except OSError, e:
                    print >> sys.stderr, 'Can\'t call %s (%s)' % (remote_check, str(e))
                
                if return_code != 0:
                    print >> sys.stderr, '%s failed' % remote_check
                    sys.exit(1)
                        
                break


if __name__ == "__main__":
    main()
