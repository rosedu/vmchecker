#!/bin/sh

set -x

linvm="/home/pso/Debian Etch PSO/Debian Etch PSO.vmx"
winvm="/home/pso/Windows Server 2003 Standard Edition/Windows Server 2003 Standard Edition.vmx"
winbuildenv=' echo \"\\program files\\Microsoft Visual Studio 8\\Common7\\Tools\\vsvars32.bat\" \&\&   \"\\program files\\Microsoft Platform SDK for Windows Server 2003 R2\\SetEnv.cmd\" /SRV32 '
localip="192.168.76.1"

getvmip()
{
    vmip=`cat /etc/vmware/vmnet8/dhcpd/dhcpd.conf | grep " $USER-$tema_os {" -A2 | tail -n1 | tr -s ' ' | cut -f2 -d' ' |tr -d ';'`
}

check_build()
{
    build_start=`cat job_output | grep -n '^checker: building$' | cut -f1 -d:`
    build_end=`cat job_output | grep -n '^checker: building ' |  cut -f1 -d:`
    if [ -z "$build_start" ] || [ -z "$build_end" ]; then
	return
    fi
    cat job_output | head -n$build_end | tail -n$[$build_end-$build_start+1] > job_building
    build_errors=`egrep '(: error)|(error: )' job_building | wc -l`
    build_warnings=`egrep '(: warning)|(warning: )' job_building | if [ "$tema_os" = "win" ]; then egrep -v "(parser[.]tab[.]|parser[.]yy[.])"; else cat; fi | wc -l`
    if [ $build_errors = 0 ]; then
	if ! [ -z "`cat job_building  | grep '^checker: building failed'`" ]; then
	    build_errors=1;
	fi
    fi
    if ! [ -z "`cat job_output | grep 'failed to build tests, exiting'`" ]; then
	build_errors=1;
    fi
}

check_bugs()
{
    bugs=`cat job_km | grep "BUG:" | wc -l`
}

check_deadline()
{
    deadline=`ssh pso@cs.pub.ro "cat public_html/Teme/0$tema_no.*.html | grep 'Termen de predare' " | cut -f2 -d'(' | cut -f1 -d')'`

    if [ -z "$deadline" ]; then 
	slip=0
	return
    fi

    deadline_s=`date --date="$deadline" +%s` 
    tema_date_s=`date --date="$1" +%s`

    if [ $tema_date_s -lt $deadline_s ]; then
	slip=0
	return
    fi
    slip=$[($tema_date_s-$deadline_s)/60/60/24]
}

basic_checks()
{
    tema_no=`echo $1 | cut -f3 -d'/' | tr -d tema`
    tema_date=`echo $1| cut -f5 -d'/'`
    
    check_deadline $tema_date $tema_no
    
    check_build 

    check_bugs 
    
    if [ $build_errors -gt 0 ] || [ $bugs -gt 0 ]; then
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
    
    
    if [ $bugs -gt 0 ]; then
	echo "-10: au fost identificate $bugs bug-uri"
    fi;

    if [ $slip -gt 0 ]; then
	if [ $slip -gt 12 ]; then
	    slip=12;
	fi 
	penalty=$[$slip*25] 
	echo "-$[$penalty/100].$[$penalty%100]: intarziere $slip zile"
    fi
    
}

run_test()
{

    if echo $1 | grep '/lin' 1>&2; then
	vm="$linvm"
	tema_os="lin"
	user="root"
    else
	vm="$winvm"
	tema_os="win"
	user="Administrator"
    fi
    
    tema_no=`echo $1 | cut -f3 -d'/' | tr -d tema`
    tema_date=`echo $1| cut -f5 -d'/'`
    echo -e "\nchecker: checking $1"

    
    #starting VM
    if ! [ -z "$lastvm" ] && [ "$lastvm" != "$vm" ]; then
	vmware-cmd "$lastvm" stop hard 1>&2;
    fi
    lastvm="$vm"
    
    retry=0;
    while true; do
        if ! /usr/bin/vmrun revertToSnapshot "$vm" 1>&2; then
	    echo "failed to start vm"
	    return 1
        fi
	sleep 1s;
        getvmip 
	if ! [ -z "$vmip" ] && ping -w1 -c1 "$vmip" 1>&2; then
	    break;
	elif [ "$retry" = "5" ]; then
	    echo "could not get ip address for $vm"
    	    return 1
	else
	    retry=$[$retry+1]
	fi
    done

    echo -e "\nkernel messages: " > job_km
    #on linux start nc to capture kernel messages
    if [ "$tema_os" = "lin" ]; then
        nc -u -l -p 6666 >> job_km &   
    else
	ssh $user@$vmip "dbgview /l job_km & sleep 3 && tail -f job_km" >> job_km &
    fi


    #copy job to VM
    if ! scp file.zip $user@$vmip:. 1>&2; then
	echo "failed to copy job to vm"
        return 1
    fi
    
    echo "unpacking ..."
    if ! ssh $user@$vmip unzip -o file.zip 2>&1; then
	echo "failed, exiting"
        return 1
    fi


    echo -e "\nchecker: building" 
    if [ "$vm" = "$linvm" ]; then
        echo "fixing file dates ..."
	if ! ssh $user@$vmip 'find . | xargs touch' 2>&1; then
    	    echo "checker: cannot touch files"
	    return 0
	fi
        if ! ssh $user@$vmip ' make kbuild' 2>&1; then
	    echo "checker: building failed"
    	    return 0
        fi
    else 
        echo "fixing file dates ..."
	if ! ssh $user@$vmip "/usr/bin/find . | xargs touch" 2>&1; then
    	    echo "checker: cannot touch files"
	    return 0
	fi
	if ! ssh $user@$vmip " $winbuildenv  \&\& nmake kbuild > __checker.bat; cmd /c __checker.bat " 2>&1; then
	    echo "checker: building failed"
	    return 0
	fi
    fi
    echo "checker: building done"

    #fetching and installing tests 
    tests=` ssh pso@cs.pub.ro "cat public_html/Teme/0$tema_no.*.html | egrep -i test.*$tema_os.zip  | sed -e 's/.*href=\".*pso\/\(.*test.*$tema_os.zip\)\" .*/\1/i'"`
    if ! scp pso@cs.pub.ro:public_html/$tests tests.zip 1>&2; then
	echo "failed to get tests, exiting"
	return 0;
    fi

    # install tests locally - we may need a local tester - do pre-building
    mkdir tests && cp tests.zip tests && cd tests && unzip -o tests.zip 1>&2 > /dev/null
    if [ -f pre-build.sh ]; then
	    sh pre-build.sh $localip $vmip
    fi
    rm tests.zip
    zip -r ../tests.zip *
    cd ..

    if ! scp tests.zip $user@$vmip:. 1>&2; then
	echo "failed to get tests, exiting"
	return 0
    fi
    if ! ssh $user@$vmip unzip -o tests.zip 1>&2; then
	echo "failed to unzip tests, exiting"
	return 1;
    fi

    timeout=120
    echo -e "\nchecker: setting test timeout to $timeout seconds"

    echo -e "\nchecker: testing"

    # in case of local testing; build and run local test
    echo -e "\n\nlocal messages:" > local_out.txt
    cd tests
    if [ -f _local_checker.sh ]; then
	    sh _local_checker.sh 1>&2 >> ../local_out.txt
    fi
    cd ..

    echo -e "\n\nvirtual machine messages:" > vm_out.txt
    if  [ "$vm" = "$linvm" ]; then
	ssh $user@$vmip ' if [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker run; else echo dont know how to run tests; fi ' 2>&1 >> vm_out.txt &
    else
	ssh $user@$vmip " if [ -f _checker.bat ]; then cmd /c _checker.bat; elif [ -f NMakefile.checker ]; then $winbuildenv \&\& nmake -f NMakefile.checker run > __checker.bat; cmd /c __checker.bat; elif [ -f _checker.sh ]; then sh _checker.sh; elif [ -f Makefile.checker ]; then make -f Makefile.checker run; else echo dont know how to run tests; fi " 2>&1 >> vm_out.txt &
    fi

    while [ $timeout -gt 0 ]; do
	if [ -z "`jobs|egrep 'Running.*ssh.*checker'`" ]; then
	    break;
	fi
	timeout=$[$timeout-1]
	sleep 1
    done
    
    cat vm_out.txt
    cat local_out.txt

    if ! [ -z "`jobs|egrep 'Running.*ssh.*checker'`" ]; then
	killall -9 "test" 1>&2 > /dev/null
	kill %1 %2 # kill nc also 
	echo -e "\nchecker: testing timeouted";
    else
	kill %1
	killall -9 "test" 1>&2 > /dev/null
	echo -e "\nchecker: testing completed (with ${timeout}s to spare)"
    fi

    return 0
}

while true; do
    #cleanup
    kill -9 `lsof  | grep "nc.*pso.*job_km" | tr -s ' ' | cut -f2 -d' ' `
    kill -9 `lsof  | grep "ssh.*pso.*job_km" | tr -s ' ' | cut -f2 -d' ' `
    kill -9 `lsof  | grep "test.*pso.*job_km" | tr -s ' ' | cut -f2 -d' ' `
    rm -f file.zip job_* tests.zip *_out.txt
    rm -fr tests

    #get next job
    tema=`ssh pso@cs.pub.ro find teme/checker -name file.zip | sort -k7 -t/ | head -n1`
    scp pso@cs.pub.ro:\'"$tema"\' . &>/dev/null 
    if ! [ -f file.zip ]; then
	if ! [ -z "$lastvm" ]; then
	    vmware-cmd "$lastvm" stop hard
	fi
	exit 1
    fi
    #filter out
    tema="`echo $tema | cut -f3-7 -d'/'`" 
    # test it
    if run_test "$tema" > job_output 2>job_errors; then
	# more automation
	basic_checks "$tema" > job_checks 2>> job_errors
	cat job_checks job_output job_km > job_results	

        # send results 
	scp job_results pso@cs.pub.ro:\'"teme/ok/$tema/NOTA"\'
	ssh pso@cs.pub.ro rm \'"teme/ok/$tema/../NOTA"\'
	ssh pso@cs.pub.ro ln -s \'"`echo $tema|rev | cut -f1 -d/|rev`/NOTA"\' \'"teme/ok/$tema/../NOTA"\'
	ssh pso@cs.pub.ro rm -f \'"teme/checker/$tema/file.zip"\'
	ssh pso@cs.pub.ro 'cd public_html/Teme/upload && ./update_grades'
	err=0
    else
	err=1
    fi
    scp job_errors pso@cs.pub.ro:.
    ssh pso@cs.pub.ro 'cat job_errors >> logs/sanctuary'
    if [ "$err" = "1" ]; then
	ssh pso@cs.pub.ro 'cat job_errors | mail -s "sanctuary: `tail -n2 job_errors|head -n1`" sanctuary@cs.pub.ro'
	exit 1
    fi
done

