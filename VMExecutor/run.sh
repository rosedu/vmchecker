#!/bin/sh

home="/home/user"
cd $home

winbuildenv="\"\\program files\\Microsoft Visual Studio 8\\Common7\\Tools\\vsvars32.bat\" &&   \"\\program files\\Microsoft Platform SDK for Windows Server 2003 R2\\SetEnv.cmd\" /SRV32 "

run_tests()
{
    timeout=120

    echo -e "\nchecker: setting test timeout to $timeout seconds"

    echo -e "\nchecker: testing"

    if  [ "$1" = "lin" ]; then
	 if [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker; else echo dont know how to run tests; fi  2>&1
    else
	if [ -f _checker.bat ]; then cmd /c _checker.bat; elif [ -f NMakefile.checker ]; then echo $winbuildenv \&\& nmake -f NMakefile.checker > __checker.bat; cmd /c __checker.bat; elif [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker ; else echo dont know how to run tests; fi  2>&1 
    fi

}

run_tests $1 >job_run 2> job_run
