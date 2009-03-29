#!/usr/bin/env python
"""Callback script executed on the tester machine
"""
import sys
import misc, vmcheckerpaths

if __name__ == "__main__":
    print '[CALLBACK] YEAH! Callback ran! sys.argv[] = %s' % str(sys.argv)
    print '[CALLBACK] test vmcheckerpaths-root: %s ' % vmcheckerpaths.root()
