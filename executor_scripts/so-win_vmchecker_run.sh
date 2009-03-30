#!/bin/sh

home=$1
cd $home

winbuildenv="\"C:\Program Files\Microsoft SDKs\Windows\v6.1\Bin\SetEnv.Cmd\""

run_tests()
{
    echo -e "\nchecker: testing"

    if [ -f _checker.bat ]; then
        echo '1'
        cmd /E:ON /V:ON /T:0E /C /c _checker.bat;
    elif [ -f NMakefile.checker ]; then
        echo '2'
        echo $winbuildenv \&\& nmake -f NMakefile.checker > __checker.bat;
        cmd /E:ON /V:ON /T:0E /C /c __checker.bat;
    elif [ -f _checker.sh ]; then
        echo '3'
        sh _checker.sh;
    elif [ -f Makefile.checker ]; then
        echo '4'
        make -f Makefile.checker;
    else echo dont know how to run tests; fi  2>&1 
}

run_tests  >job_run 2> job_run
