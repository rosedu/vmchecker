#!/bin/sh

#runs inside vm

home=$1
winbuildenv="\"C:\Program Files\Microsoft SDKs\Windows\v6.1\Bin\SetEnv.Cmd\""

cd $home

get_vm_ip()
{
	echo "Adresa IP a masinii virtuale este:"
	ipconfig |grep "IP Address"|cut -d ':' -f 2 |cut -d " " -f 2|head -n 1 2>&1
}


install_job()
{
	echo "homework contents: "
	unzip -l file.zip 2>&1
	echo "unpacking ..."
	# note stdout redirected to stderr: do not output file.zip contents
	# contents printed with more info above with "unzip -l"
	unzip -o file.zip 1>&2
	return $?
}

build_job()
{
	echo -e "\nchecker: building"
	export TMP="c:\\cygwin\\tmp"
	echo "fixing file dates ..."
	/usr/bin/find . | xargs touch 2>&1
	echo $winbuildenv \&\& nmake /nologo build > __checker.bat; cmd /E:ON /V:ON /T:0E /C  __checker.bat  2>&1
	if [ "$?" != 0 ]; then
		echo "checker: building failed"
		return 1
	fi

	echo "checker: building done"
	return 0
}

install_tests()
{
	echo -e "\ntests.zip size: " $(stat -c%s "tests.zip")
	# note stdout redirected to stderr: do not output tests.zip contents
	# (large output)
	unzip -o tests.zip 1>&2
	return $?
}

build_tests()
{
	if [ -f NMakefile.checker ]; then echo $winbuildenv \&\& nmake /nologo -f NMakefile.checker build-$1 > __checker.bat; cmd /E:ON /V:ON /T:0E /C /c __checker.bat;
       	elif [ -f Makefile.checker ]; then make -f Makefile.checker build-$1;
       	else echo dont know how to build tests;
       	fi  2>&1

	return  0
}

check_job()
{
	get_vm_ip ;

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

	build_job; err=$?
	if [ $err != 0 ]; then
		return $err
	fi

	build_tests "post"; err=$?
	if [ $err != 0 ]; then
		return $err
	fi


	return 0
}

main()
{

	# test it
	touch build-stdout.vmr build-stderr.vmr
	echo 'checker: building' >> build-stdout.vmr
	check_job > build-stdout.vmr 2>build-stderr.vmr;  err=$?

	if [ $err -gt 1 ]; then
		echo "this looks like a checker system error, admins should be notified" >>build-stderr.vmr
	fi

	return $err
}

main
