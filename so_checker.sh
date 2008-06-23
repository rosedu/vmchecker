#!/bin/sh

set -x

linvm="/home/so/Debian_Etch/Debian Etch.vmx"
winvm="/home/so/WinXP_SP2/Windows XP Professional.vmx"
winbuildenv=' echo \"\\program files\\Microsoft Visual Studio 8\\Common7\\Tools\\vsvars32.bat\" \&\&   \"\\program files\\Microsoft Platform SDK for Windows Server 2003 R2\\SetEnv.cmd\" /SRV32 '

getvmip()
{
    vmip=`cat /etc/vmware/vmnet8/dhcpd/dhcpd.conf | grep " $USER-$job_os {" -A2 | tail -n1 | tr -s ' ' | cut -f2 -d' ' |tr -d ';'`
}

check_build()
{
    build_start=`cat job_output | grep -n '^checker: building$' | cut -f1 -d:`
    build_end=`cat job_output | grep -n '^checker: building ' |  cut -f1 -d:`
    if [ -z "$build_start" ] || [ -z "$build_end" ]; then
	build_errors=1
	build_warnings=0
	return
    fi
    cat job_output | head -n$build_end | tail -n$[$build_end-$build_start+1] > job_building
    build_errors=`egrep '(: error)|(error: )' job_building | wc -l`
    build_warnings=`egrep '(: warning)|(warning: )' job_building | if [ "$job_os" = "win" ]; then egrep -v "(parser[.]tab[.]|parser[.]yy[.])"; else cat; fi | wc -l`
    if [ $build_errors = 0 ]; then
	if ! [ -z "`cat job_building  | grep '^checker: building failed'`" ]; then
	    build_errors=1;
	fi
    fi
    if ! [ -z "`cat job_output | grep 'failed to build tests, exiting'`" ]; then
	build_errors=1;
    fi
}

check_deadline()
{
    deadline=`ssh $USER@cs.pub.ro "cat public_html/Teme/0$job_no.*.html | grep 'Termen de predare' " | cut -f2 -d'(' | cut -f1 -d')'`

    if [ -z "$deadline" ]; then 
	slip=0
	return
    fi

    deadline_s=`date --date="$deadline" +%s` 
    job_date_s=`date --date="$1" +%s`

    if [ $job_date_s -lt $deadline_s ]; then
	slip=0
	return
    fi
    slip=$[($job_date_s-$deadline_s)/60/60/24]
}

post_checks()
{
    check_deadline $job_date $job_no
    
    check_build 
    
    if [ $build_errors -gt 0 ]; then
	echo -e "0\n"
    else 
	echo -e "ok\n"
    fi

    if [ $build_errors -gt 0 ]; then
	echo "-10: tema nu se compileaza"
    fi

    if [ $build_warnings -gt 0 ]; then
	echo "-1: compilarea a produs $build_warnings warning-uri"
    fi
    
    if [ $slip -gt 0 ]; then
	if [ $slip -gt 12 ]; then
	    slip=12;
	fi 
	penalty=$[$slip*25] 
	echo "-$[$penalty/100].$[$penalty%100]: intarziere $slip zile"
    fi
    
}

try_start_vm()
{
        if ! /usr/bin/vmrun revertToSnapshot "$vm" 1>&2; then
	    echo "failed to start vm"
	    return 1
        fi
	sleep 1s;
        getvmip 
	if ! [ -z "$vmip" ] && ping -w1 -c1 "$vmip" 1>&2; then
	    return 0
	fi
	echo "vm does not respond"
	return 1
}

start_vm()
{
    if ! [ -z "$lastvm" ] && [ "$lastvm" != "$vm" ]; then
	vmware-cmd "$lastvm" stop hard 1>&2;
    fi
    lastvm="$vm"
    
    retry=0;
    while [ 5 -gt $retry ]; do
	retry=$[$retry+1]
	if try_start_vm; then
	    break;
	fi
    done
    
    return 0
}

install_job()
{
    if ! scp file.zip $user@$vmip:. 1>&2; then
	echo "failed to copy job to vm"
        return 2
    fi
    
    echo "unpacking ..."
    if ! ssh $user@$vmip unzip -o file.zip 2>&1; then
	echo "failed, exiting"
        return 2
    fi
    
    return 0
}

build_job()
{
    echo -e "\nchecker: building" 
    if [ "$vm" = "$linvm" ]; then
        echo "fixing file dates ..."
	if ! ssh $user@$vmip 'find . | xargs touch' 2>&1; then
    	    echo "checker: cannot touch files"
	    return 2
	fi
        if ! ssh $user@$vmip ' make build' 2>&1; then
	    echo "checker: building failed"
    	    return 1
        fi
    else 
        echo "fixing file dates ..."
	if ! ssh $user@$vmip "/usr/bin/find . | xargs touch" 2>&1; then
    	    echo "checker: cannot touch files"
	    return 2
	fi
	if ! ssh $user@$vmip " $winbuildenv  \&\& nmake build > __checker.bat; cmd /c __checker.bat " 2>&1; then
	    echo "checker: building failed"
	    return 1
	fi
    fi
    echo "checker: building done"
    
    return 0
}

install_tests()
{
    tests=` ssh $USER@cs.pub.ro "cat public_html/Teme/0$job_no.*.html | egrep -o \"wiki/[^ ]*Test[^ ]*_$job_os[^ ]*zip\""`

    if [ -z "$tests" ]; then
        tests=` ssh $USER@cs.pub.ro "cat public_html/Teme/0$job_no.*.html | egrep -o \"wiki/[^ ]*Test[^ ]*zip\""`
    fi

    
    if [ -z "$tests" ]; then
	echo "no tests found"
	return 2
    fi

    if ! scp $USER@cs.pub.ro:public_html/$tests tests.zip 1>&2; then
	echo "failed to download tests"
	return 2
    fi

    if ! scp tests.zip $user@$vmip:. 1>&2; then
	echo "failed to upload tests"
	return 2
    fi

    if ! ssh $user@$vmip unzip -o tests.zip 1>&2; then
	echo "failed to unzip tests"
	return 2
    fi

    return 0;
}

build_tests()
{
    if  [ "$vm" = "$linvm" ]; then
	ssh $user@$vmip " if [ -f Makefile.checker ]; then make -f Makefile.checker build-$1; else echo dont know how to build tests; fi " 2>&1 
    else
	ssh $user@$vmip " if [ -f NMakefile.checker ]; then $winbuildenv \&\& nmake -f NMakefile.checker build-$1 > __checker.bat; cmd /c __checker.bat; elif [ -f Makefile.checker ]; then make -f Makefile.checker build-$1; else echo dont know how to build tests; fi " 2>&1 
    fi

    if [ "$?" != 0 ]; then
	if [ "$job_no" = "3" ] && [ "$vm" = "$winvm" ] && [ "$1" = "pre" ]; then
	    return 2
	fi
	return 1
    fi
    
    return  0
}

run_tests()
{
    timeout=120
    echo -e "\nchecker: setting test timeout to $timeout seconds"

    echo -e "\nchecker: testing"

    if  [ "$vm" = "$linvm" ]; then
	ssh $user@$vmip ' if [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker; else echo dont know how to run tests; fi ' 2>&1 &
    else
	ssh $user@$vmip " if [ -f _checker.bat ]; then cmd /c _checker.bat; elif [ -f NMakefile.checker ]; then $winbuildenv \&\& nmake -f NMakefile.checker > __checker.bat; cmd /c __checker.bat; elif [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker ; else echo dont know how to run tests; fi " 2>&1 &
    fi

    while [ $timeout -gt 0 ]; do
	if [ -z "`jobs|egrep 'Running.*ssh.*checker'`" ]; then
	    break;
	fi
	timeout=$[$timeout-1]
	sleep 1
    done
    
    if ! [ -z "`jobs|egrep 'Running.*ssh.*checker'`" ]; then
	kill %1 
	echo -e "\nchecker: testing timeouted";
    else
	kill %1
	echo -e "\nchecker: testing completed (with ${timeout}s to spare)"
    fi

    return 0
}

check_job()
{

    user=so
    if echo $1 | grep '/lin' 1>&2; then
	vm="$linvm"
	job_os="lin"
    else
	vm="$winvm"
	job_os="win"
    fi
    job_no=`echo $1 | cut -f3 -d'/' | tr -d tema`
    job_date=`echo $1| cut -f5 -d'/'`
    echo -e "\nchecker: checking $1"

    start_vm; err=$?
    if [ $err != 0 ]; then
	return $err
    fi

    install_job; err=$?
    if [ $err != 0 ]; then
	return $err
    fi

    install_tests; err=$?
    if [ $err != 0 ]; then
	return $err
    fi

    build_tests "pre"; err=$?
    if [ $err != 0 ]; then
	return $err
    fi

    build_job "pre"; err=$?
    if [ $err != 0 ]; then
	return $err
    fi
    
    build_tests "post"; err=$?
    if [ $err != 0 ]; then
	return $err
    fi

    run_tests; err=$?
    if [ $err != 0 ]; then
	return $err
    fi

    return 0
}

while true; do
    #cleanup first; if we are interrupted we migh leave garbage behind
    rm -f job_* file.zip tests.zip

    #get next job
    job=`ssh $USER@cs.pub.ro find teme/checker -name file.zip | sort -k7 -t/ | head -n1`
    if ! [ -z "$job" ]; then
	scp $USER@cs.pub.ro:\'"$job"\' . &>/dev/null 
    fi;
    if [ -z "$job" ] || ! [ -f file.zip ]; then
	if ! [ -z "$lastvm" ]; then
	    vmware-cmd "$lastvm" stop hard
	fi
	exit 1
    fi
    #filter out
    job="`echo $job | cut -f3-7 -d'/'`" 

    # test it
    check_job "$job" > job_output 2>job_errors;  err=$?
    post_checks "$job" > job_checks 2>> job_errors
    cat job_checks job_output > job_results; 
    if [ $err -gt 1 ]; then
        echo "this looks like a checker system error, admins will be notified" >>job_results
    fi;

    # send results 
    scp job_results $USER@cs.pub.ro:\'"teme/ok/$job/NOTA"\'; 
    ssh $USER@cs.pub.ro rm \'"teme/ok/$job/../NOTA"\'
    ssh $USER@cs.pub.ro ln -s \'"`echo $job|rev | cut -f1 -d/|rev`/NOTA"\' \'"teme/ok/$job/../NOTA"\'
    ssh $USER@cs.pub.ro rm -f \'"teme/checker/$job/file.zip"\'
    ssh $USER@cs.pub.ro 'cd public_html/Teme/upload && ./update_grades'

    #logs
    scp job_errors $USER@cs.pub.ro:.
    ssh $USER@cs.pub.ro 'cat job_errors >> logs/sanctuary'
    
    #signal errors
    if [ $err -gt 1 ]; then
	ssh $USER@cs.pub.ro 'cat job_errors | mail -s "sanctuary: `tail -n2 job_errors|head -n1`" tavi@cs.pub.ro'
    fi

done

