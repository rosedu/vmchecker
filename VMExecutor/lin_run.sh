#!/bin/sh

home=$1
cd $home

run_tests()
{
    echo -e "\nchecker: testing"

    if [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker; else echo dont know how to run tests; fi  2>&1
}

run_tests >job_run 2> job_run
