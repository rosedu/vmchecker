#! /usr/bin/env python2.5

import misc
import os

def main():
    root = misc.vmchecker_root()
    back = root + "/back"
    for hw in os.listdir(back):
        print ("hw: " + hw)

if __name__ == "__main__":
    main()
