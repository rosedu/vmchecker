#!/bin/sh

home=$1
cd $home

winbuildenv="\"C:\Program Files\Microsoft Visual Studio 9.0\VC\vcvarsall.bat\""

run_tests()
{
    echo -e "\nchecker: testing"

    if [ -f _checker.bat ]; then
        cmd /E:ON /V:ON /T:0E /C  _checker.bat;
    elif [ -f NMakefile.checker ]; then
        echo $winbuildenv \&\& nmake /nologo -f NMakefile.checker run > __checker.bat;
        cmd /E:ON /V:ON /T:0E /C  __checker.bat;
    elif [ -f _checker.sh ]; then
        sh _checker.sh;
    elif [ -f Makefile.checker ]; then
        make -f Makefile.checker;
    else echo dont know how to run tests; fi  2>&1 
}

run_tests  >run-stdout.vmr 2> run-stderr.vmr
