#!/bin/sh

#
# [vmchecker] test run batch script - runs tests
#

# run setup scripts
## N/A on Linux (for now)

# run tests
make -f Makefile.checker pre-run
make -f Makefile.checker run
make -f Makefile.checker post-run
