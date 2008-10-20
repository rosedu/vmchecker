#! /usr/bin/env python2.5

import misc
import os
import check_config

def main():
    root = misc.vmchecker_root()
    back = root + "/back"
    for hw in os.listdir(back):
        print ("hw: " + hw)
        hwdir = back + "/" + hw
        for name in os.listdir(hwdir):
            print ("\t name: " + name)
            namedir = hwdir + "/" + name
            dates = os.listdir(namedir)
            dates.sort()
            for date in dates:
                print ("mata: " + date)
                datedir = namedir + "/" + date
                inifile = datedir + "/" + date + name + hw + ".ini"
                print (inifile);
                

                try:
                    os.stat(inifile)
                except OSError:
                    continue
                print ("\t\t latest date of upload: " + date + " f:" + inifile)
                remote_check = os.path.join(os.path.dirname(sys.argv[0]), 
                                            'remote_check.py')
                try:
                    return_code = subprocess.call([remote_check, inifile])
                except OSError, e:
                    print >> sys.stderr, 'Can\'t call %s (%s)' % (remote_check, str(e))
                    
                if return_code != 0:
                    print >> sys.stderr, '%s failed' % remote_check
                    sys.exit(1)
                        
                break


if __name__ == "__main__":
    main()
