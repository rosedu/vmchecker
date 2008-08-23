#!/bin/bash

#
# [vmchecker] deploy script:
#	* copy assigment and test archive to remote server - use SSH
#	* copy build and run batch scripts
#	* run "build batch script" to compile sources
#	* run "run batch script" to run tests
#	* retrieve results
#
# everything is hardcoded:
#	* ASSIGNMENT is assigment archive
#	* TEST is test arhive
#	* BUILD_SCRIPT is "build batch script"
#	* RUN_SCRIPT is "run batch script"
#	* BUILD_OUTPUT is "build batch script" output
#	* RUN_OUTPUT is "run batch script" output
#	* VM_ADDRESS is virtual machine's IP address
#	* VM_USER is virtual machines's username (public key connection is assumed)
#	* VM_PATH is the location where everything (building, running) happens on the virtual machine
#	* VM_SCRIPT_COMMAND is the command which runs the scripts
#

ASSIGNMENT=file.zip
TESTS=tests.zip
BUILD_SCRIPT=build.bat
RUN_SCRIPT=run.bat
BUILD_OUTPUT=build.txt
RUN_OUTPUT=run.txt
VM_ADDRESS=192.168.68.128
VM_USER=Administrator
VM_PATH=/home/${VM_USER}
VM_SCRIPT_COMMAND="cmd /c"

# debug on or off
DEBUG_=1

function copy_file_to_vm()
{
	_file=$1

	scp ${_file} ${VM_USER}@${VM_ADDRESS}:${VM_PATH}
}

function copy_file_from_vm()
{
	_file=$1

	scp ${VM_USER}@${VM_ADDRESS}:${VM_PATH}/${_file} .
}

function unpack_in_vm()
{
	_file=$1

	ssh ${VM_USER}@${VM_ADDRESS} "unzip -o ${_file}"
}

function run_script_in_vm()
{
	_script=$1
	_output=$2

	ssh ${VM_USER}@${VM_ADDRESS} "${VM_SCRIPT_COMMAND} ${_script} > ${_output} 2>&1"
}

function main()
{
	copy_file_to_vm ${ASSIGNMENT}
	copy_file_to_vm ${TESTS}
	copy_file_to_vm ${BUILD_SCRIPT}
	copy_file_to_vm ${RUN_SCRIPT}

	unpack_in_vm ${ASSIGNMENT}
	unpack_in_vm ${TESTS}

	run_script_in_vm ${BUILD_SCRIPT} ${BUILD_OUTPUT}
	run_script_in_vm ${RUN_SCRIPT} ${RUN_OUTPUT}

	copy_file_from_vm ${BUILD_OUTPUT}
	copy_file_from_vm ${RUN_OUTPUT}
}

# verbose command printing in case debug is on
if test ${DEBUG_} -eq 1; then
	set -x
fi

# call main
main

exit 0
