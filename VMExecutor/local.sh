#!/bin/sh

localip=$1
vmip=$2

install_local()
{
    # install tests locally - we may need a local tester - do pre-building
    mkdir tests && cp tests.zip tests && cd tests && unzip -o tests.zip 1>&2 > /dev/null
    if [ -f pre-build.sh ]; then
	    sh pre-build.sh $localip $vmip
    fi
    rm tests.zip
    zip -r ../tests.zip *
    cd ..

    # in case of local testing; build and run local test
    echo -e "\n\nlocal messages:" > local_out.txt
    cd tests
    if [ -f _local_checker.sh ]; then
	    sh _local_checker.sh 1>&2 >> ../local_out.txt
    fi
    cd ..
}

install_local