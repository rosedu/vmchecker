#!/bin/sh

#
# [vmchecker] build shell script - compiles assigments and tests
#

# run setup scripts
## N/A on Linux (for now)

# build assignment
make pre-build
make build
make post-build

# build tests
make -f Makefile.checker pre-build
make -f Makefile.checker build
make -f Makefile.checker post-build
