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
                zipfile = datedir + "/" + "file.zip"
                print (os.stat(zipfile))
                if os.stat(zipfile) != None:
                    print ("\t\t latest date of upload: " + date)
                    check_config.check_config(name, hw, datedir + "/file.zip")
                    break


if __name__ == "__main__":
    main()
