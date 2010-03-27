#!/bin/sh

home=$1
cd $home

run_tests()
{
    echo -e "\nchecker: testing"

    if [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker; else echo dont know how to run tests; fi  2>&1
}

run_tests > run-stdout.vmr 2> run-stderr.vmr
