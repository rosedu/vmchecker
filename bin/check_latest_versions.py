#! /usr/bin/env python2.5

import misc
import os

root = misc.vmchecker_root()
back = root + "/back"
for hw in os.listdir(back):
    print ("hw: " + hw)
