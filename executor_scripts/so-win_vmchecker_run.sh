#!/bin/sh

home=$1
cd $home

winbuildenv="\"C:\Program Files\Microsoft SDKs\Windows\v6.1\Bin\SetEnv.Cmd\""

run_tests()
{
    echo -e "\nchecker: testing"

    if [ -f _checker.bat ]; then
        cmd /E:ON /V:ON /T:0E /C /c _checker.bat;
    elif [ -f NMakefile.checker ]; then
        echo $winbuildenv \&\& nmake /nologo -f NMakefile.checker > __checker.bat;
        cmd /E:ON /V:ON /T:0E /C /c __checker.bat;
    elif [ -f _checker.sh ]; then
        sh _checker.sh;
    elif [ -f Makefile.checker ]; then
        make -f Makefile.checker;
    else echo dont know how to run tests; fi  2>&1 
}

run_tests  >job_run 2> job_run
